# Reassessment Slice 4 retention plan — approval candidate

Documentation only, 2026-09-23. No cap is changed, corpus created, application/test
executed or implementation resumed. This plan covers Slice 4 only. It replaces
the earlier suggested generic fresh 64 MiB allocation with the bounded allocation
below; the earlier discrepancy remains historical and unchanged.

## Authority and meaning of the ceiling

Verified administrative HEAD: `8f0c6ea92d973cc77acc4d4cded9dc86eb826581`.
Accepted Slice 3 implementation: `433077d717719921d89fe5f882c83bf93f55c18e`;
acceptance: `fd37f93a4f5d35d7a4030ff62bfb56117f68a9f6`. Both are ancestors.
[Discrepancy report](2026-09-23-reassessment-slice4-retention-discrepancy.md)
is unchanged at SHA-256
`e35f2d15ac8449813a9e1ef1736b40a28f71952d1c7fe25a19e5e12729dc2ec2`.

Governing [RESOURCES.md](2026-09-23-reassessment-preparation/RESOURCES.md),
“Future qualification obligations,” lines 84–91, says exactly:

> The existing safety ceilings (512 MiB address space, 64 MiB retained runtime corpus,
> 30 seconds per command) are not raised or newly measured here.

And:

> Fixture/recovery archive bytes are preparation
> material, separately measured from a retained runtime corpus. Allocate immutable
> runtime runs on approved ext4 locations; stop before exhausting an approved corpus
> budget and request an explicit evidence-retention plan if necessary. Do not delete
> earlier runtime evidence to manufacture capacity.

Its SHA-256 is `63574f48e4576b92245574ec8fc2b794e381df4479091dba6e9197b6c36964a9`.
The exact-package accounting-policy.json has
`unchanged_safety_ceilings.retained_corpus_bytes = 67108864`
and SHA-256 `ffabc52e0d601502149f2cda4d221f599a31f0922a0f6d3fb1d34e7037d5a564`.

Thus the named unit is a **retained runtime corpus**, not a command or run. These
clauses do not explicitly define a repository-wide/lifetime aggregate over every
corpus, nor authorize unlimited separate corpora. Accepted Slices 1–3 conservatively
sum multiple runs as one historical corpus. A new directory does not reset that
accounting. The 67,108,864-byte ceiling is nearly exhausted, not already exceeded.
This plan requests an explicit, finite combined-retention amendment; it does not
claim a previously authorized per-run reset. If the ceiling is read globally,
the exact required exception is the same H+Q bound below. Neither interpretation
permits an unbounded succession of fresh corpora.

## Historical corpus H: immutable in place

H is the regular files directly in the 279 manifest directories enumerated by
`corpus-inventory.json` in the committed
[retention evidence archive](2026-09-23-reassessment-slice4-retention-evidence.zip),
SHA-256 `ee2982a7fae7bc4e4fe379f1d2f94dc0776be532cacf6d3169bf87f15c25a1a8`.
That archive's four payload commitments were verified. Fresh reads found:

| Exact containing root | Result directories | Regular files | Logical bytes | Fresh tree SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `/tmp/nr-slice1-runtime-xmug1php` | 0 | 0 | 0 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |
| `/tmp/nr-slice1-final-ce_xngoo` | 213 | 1489 | 50,215,901 | `cf45da9fde102dcac5160390c6e4bfb30db1dc66eab491e97218c2b1fd496f24` |
| `/tmp/nr-slice1-candidate-uz9ieotx` | 12 | 84 | 2,774,263 | `e75ee529130fdb160ad8599ad9b9709d404ffcb0c2b0788156c7be09aa3eda1c` |
| `/tmp/nr-slice1-verified-xbs3khdg` | 40 | 280 | 9,200,793 | `62227dc66b0fc67b333ddd0bf37a04a214d4ac762cd4543ee37206f567946bc9` |
| `/tmp/nr-slice1-release-check-00p0z3uz` | 12 | 84 | 2,774,263 | `79970052011321a8e98c06a19b85c83612c33f5a6671a4d0be3ca35a24dc1e58` |
| `/tmp/nr-slice2-check-n5zs06y5` | 2 | 14 | 468,768 | `8a1015379aa530a821439d8530ce2ebed87bf6b6bea21ca1147e5ca8368c0c09` |

Total: **1,951 regular files, 65,433,988 logical bytes**, with **69,836,800
allocated regular-file bytes** on the present filesystem. Per-root tree hashes
commit a canonical JSON array of `[relative_path, byte_count, sha256(file_bytes)]`
records, sorted by UTF-8 path bytes; JSON is ASCII-escaped, compact comma/colon
separators, no trailing LF. The zero-file tree is `[]`. The combined equivalent
array uses absolute paths, with SHA-256
`0ae693f44e5ca9edf0ab94e9958a436ab32e74a12d43c09703c171c89d62dd14`.
These are new read-only commitments, not claims that an earlier file-level
inventory existed. The older directory list plus this algorithm permits exact
re-enumeration and verification without a new sidecar file.

Two historical adverse symlinks are preserved without following or repairing:
- `/tmp/nr-slice1-final-ce_xngoo/pytest/test_persistent_hostile_twins_0/w/build.json`
  → `/tmp/nr-slice1-final-ce_xngoo/pytest/test_persistent_hostile_twins_0/outside`.
- `/tmp/nr-slice1-final-ce_xngoo/pytest/test_verifier_never_follows_me0/bundle/result.json`
  → `/mnt/d/operation-house-keeping/docs/superpowers/reports/2026-09-15-bounded-decision-workflow-candidate-package.json`.

Their text/role is retained as adverse evidence; target bytes are not a valid
bundle dependency or additional copy charged to H. Intentionally malformed and
incomplete evidence remains such; tree integrity does not assert semantic validity.

No deletion, relocation, recompression, chmod/chown, overwrite, pytest reuse of old
basetemps or cleanup of these roots is permitted. The H write budget is **zero**.
Before later work, verify the directory inventory and tree commitments again.
Existing exact seven-file historical bundle material also remains recoverable
through the committed approved package and its prior-recovery commitments; a
reference to that package does not establish recovery of every historical fault
file. H itself remains the location for those originals. Loss of a required H
file stops work; a hash alone cannot recover it. Temporary-root lifetime and
external machine cleanup remain a custody limitation, not a durability promise.

The six roots also contain **1,074,767,030 bytes of other regular files** outside
those result directories: respectively 2,280,568; 1,037,157,325; 5,273,730;
16,945,026; 6,118,911; and 6,991,470 bytes in table order. These existing inputs,
source/dependency copies and other artifacts were excluded by the accepted H
inventory. They are disclosed, preserved and not silently claimed to fit 64 MiB.
No historical side material is reclassified, copied or modified by this plan.

## Proposed new corpus Q and finite allocation

Exact proposed root (currently absent; parent is ext4):
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/nr-slice4-qualification-r1`.

Identity: `reassessment-slice4-qualification/r1`, bound to this plan's eventual
digest, owner approval record, accepted implementation, package and H commitments.
Maximum **all new Slice 4 material: 33,554,432 bytes (32 MiB)**. This includes
every retained and temporary regular-file copy, malformed/incomplete bundle,
input, log, refusal, recovery extraction and archive, even a final evidence copy
outside Q. No unaccounted /tmp spill or duplicate repository archive is allowed.
The following category ceilings are conjunctive; there is no automatic borrowing:

| Category | Cap bytes | Basis |
| --- | ---: | --- |
| Initial output/control bundle slots | 14,680,064 | Fourteen slots × unchanged 1 MiB bundle bound |
| Failed attempts and repaired rerun outputs | 4,194,304 | Four further 1 MiB slots; failures remain retained |
| Bound inputs, fixture variants and necessary scratch | 6,291,456 | Six 1 MiB capture-equivalent slots; exact shared members may avoid duplicate storage |
| Streams, refusals and detailed work logs | 1,048,576 | Bounded aggregate raw stdout/stderr/diagnostics; no assumption that logs compress |
| Standalone recovery copies | 2,097,152 | Two complete 1 MiB extractions/copies |
| Corpus indexes, reservation records and recovery receipts | 1,048,576 | Bounded append-only manifests and verification records |
| Optional evidence archives and every export copy | 4,194,304 | Copy/export budget, not assumed compression savings |
| **All new material / temporary logical high-water** | **33,554,432** | Sum of categories; deleted data never creates a planned rerun allowance |

The fourteen initial slots are six core bundles (admitted evaluation, standalone
replay, rehashed forged-result control, withholding evaluation, and the affected
legacy evaluate/replay pair), five separately retained substitutions (authority,
build, policy, required closure and profile), and three publication-fault states
(write/interruption, file-fsync, directory/parent durability). Unsafe-path and
no-overwrite checks should reuse immutable inputs and produce bounded logs rather
than gratuitous new copies. This scheduling reservation does not replace the
Slice 4 acceptance obligations or make a failed case pass.

The earlier **2,061,074-byte** core projection is included inside these slots:
419,137 + 419,137 + 419,137 + 334,895 + 468,768. It excludes four new manifests.
Four full approved manifest reservations add **65,536**, giving **2,126,610**
before faults, substitutions and repairs. Slot caps deliberately use the unchanged
complete 1 MiB bound rather than freezing today's build size or merely multiplying
that specimen by an unexplained factor. The four repair slots and two recovery
copies bound further attempts; they are not unlimited retries. If affected
regressions, additional fault artifacts, input versions or repairs need more slots
or bytes, stop with their exact demand. The plan does not guarantee all possible
regression selections fit.

All extractions and copied inputs count in addition to their archives/originals.
No hard-link/reflink or compression discount applies to logical charges. An archive
must reserve its full uncompressed member sum, framing and any simultaneous output
copy within the export category and total. A full Q archive will generally not fit
4 MiB: it is not authorized by default. Keep raw Q recoverable in place and export
only a bounded explicitly enumerated set with exact source references. Truncation
or omission of required recovery material is not a solution to an export refusal.
No new dependency/environment installation or unbudgeted checkout copy is included.

## Combined accounting and stop rules

- H logical bytes: **65,433,988**; new H writes: **0**.
- Q all-copy logical ceiling, including scratch/high-water: **33,554,432**.
- Explicit proposed H+Q maximum: **98,988,420 bytes**, which is **31,879,556
  bytes above** the former 67,108,864-byte cumulative ceiling.
- Including the separately disclosed existing side material in these six roots:
  **1,173,755,450 logical bytes** at maximum H+Q. This is not a whole-machine
  disk inventory or a retroactive enlargement of H.
- No additional temporary reserve exists outside Q. Copying a file before its
  predecessor is retained consumes both allowances; no cleanup is presumed.

For physical allocation, propose at most **4,096 regular files and 512 directories**
in Q and a **54,525,952-byte (52 MiB) allocated-space reservation**: 32 MiB payload
plus less than 16 MiB of 4 KiB file rounding plus 4 MiB reserved for indexes,
directory allocation and filesystem overhead. The arithmetic upper estimate for
payload plus maximum file tail padding plus that overhead is 54,521,856 bytes.
The overhead is a planning reserve, not a guarantee about ext4 metadata or journal
durability. Sparse files, compression or shared extents do not manufacture capacity.
Other file types are limited to explicitly recorded adverse controls and their
metadata also consumes that physical reserve; special devices/FIFOs are never
opened as data or followed into external material.

Before creation and each write-producing command, require at least the remaining
physical reservation as filesystem available space, and independently reserve
worst-case new file/copy/log growth against every logical category and total.
Record actual allocated blocks, directory usage, counts and filesystem available
space. Stop before exceeding any reserve; if overhead cannot be bounded or free
space falls, stop without deleting existing evidence. A concurrent external writer
can still cause an honest I/O refusal; free-space measurement is not a guarantee.
The filesystem reported **870,093,316,096 available bytes**
during this read-only preparation, block size 4,096. Recheck at execution time.
H's allocated regular files plus the Q physical reservation total **124,362,752
bytes**, excluding already-existing side material and H directory metadata.
Existing bytes already consume space and are not charged again as new free-space
demand. No global disk-capacity claim follows.

Before an attempt, append its exact argv/build/inputs, output paths and worst-case
reservation to the bounded ledger; do not start if its counts are unknown or do
not fit. A harness must route pytest basetemp, streams, faults and recovery copies
to Q; default pytest retention/cleanup must not delete failed evidence. Bounded
stream capture stops an overproducing process while preserving its actual prefix
and an explicit incomplete-output record, never a fabricated complete log.
Reserve termination/error evidence before starting. A command's lower operational
guards still apply independently. No category exhaustion implies permission to
open r2, discard r1 or borrow from historical headroom.

Unchanged: component/input/closure/result/trace/bundle limits, complete four-revision
ancestry, 128 objects, eight contexts, actual build identity, work/JSON/rational
bounds, 512 MiB address space, 30 seconds per command, ext4 boundary and all legacy
policies. This amendment concerns qualification retention scope only, not a new
production application resource-policy object or its committed digest.

## Custody, commitments and recovery

After approval only, create Q exclusively with no-overwrite semantics. If the exact
root exists, inspect and stop rather than reuse it or choose an implicit new root.
Create an initial immutable identity record with this plan, approval and parent H
digests. Every attempt gets a unique monotonically numbered subdirectory; no latest
symlink or mutable expected-result path. Application publication retains its own
seven-file, manifest-last, safe-path rules.

Append bounded inventory records after each attempt: exact relative name, type,
byte size, SHA-256 for regular files, link target for adverse symlinks, build/argv,
exit and stream commitments, reservation/actual charges, completeness and parent
record digest. New inventory revisions refer to their predecessors, never rewrite
the failed attempt. Final corpus manifest names all attempts, inputs, outputs,
physical-work evidence and recovery copies. It must distinguish complete bundles,
incomplete states, refused operations and historical reused evidence.

Use captured input bytes for real computation. Oracle/expected outputs remain
assertions, not runtime calculations. Recover each required input from Q or an
explicit committed recovery member or H path verified byte-for-byte; no original
unretained scratch, cache, network, digest-only content or implicit global fixture
pool is allowed. Referencing identical evidence is permitted only after exact
recovery and commitment checking. Original failures and altered adversarial copies
remain separately committed, not substituted for one another.

Recovery checks reserve their extra copies first. Verify inventory and all members,
reconstruct from explicit retained content at an isolated Q location, and retain
the actual verification/semantic-replay result. Semantic replay must not access
the original inputs or accept caller-supplied computed results. Verification of
bytes alone is not semantic replay. No stronger custody, authentication, predictive
accuracy, power-loss or cross-platform claim is made.

## Owner decision

Approve this exact one-time retention amendment: freeze H in place with zero new
writes; authorize Q only at the named root, capped at 33,554,432 logical bytes with
the category/count/physical reservations above; expressly permit the combined
98,988,420-byte H+Q maximum. Also approve resuming the already-authorized Slice 4
implementation and its bounded qualification under this plan. This is an explicit
exception to the cumulative scope previously used, not a directory-based reset.
No operational cap or corpus is changed by this proposal.

Starting inventory was 4,776 Git-enumerated regular files and 3,499 untracked
paths. The earlier 4,773-file inventory remains byte-identical, the three later
committed documents are unchanged, and the only newly untracked path is this plan.
Links, arithmetic, ending marker and whitespace were checked. HEAD is unchanged.

Subsequent slices, the full 180-command proof and final release remain separately
gated. No automatic cleanup or future-corpus entitlement is granted. This turn
creates only this plan; historical evidence, tracked sources, runtime artifacts,
dependencies, backend contracts and ledger remain unchanged. No tests, production
edits, new runtime corpus, commits or remote operations are performed.

END OF REASSESSMENT SLICE 4 RETENTION PLAN — OWNER APPROVAL REQUIRED.
