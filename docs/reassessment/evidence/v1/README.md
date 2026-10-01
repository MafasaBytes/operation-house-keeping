# Accepted reassessment evidence supplement — local retention

2026-10-01. This supplement retains the manifest-selected acceptance evidence
and adverse history. It is not a portable runtime or a publication release.
The local retention commit is administrative; it does not replace the historical
source and execution identities in the [acceptance record](../../../superpowers/reports/2026-09-30-reassessment-slice5-and-final-owner-acceptance.md).

## Exact retained artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| [Indexed package](reassessment-release-evidence-v1.pack) | 76,298,002 | `b886da2001fd1c3e8b69e5aea448972bf5e90cc50a9bcbd0989efd4c6385137e` |
| [Original verification receipt](reassessment-release-evidence-v1-verification.json) | 41,316 | `521c8ccc502069f5e69c322676a8ebe0c8c0723f0928fc72fc203d5997e3a627` |

The frozen [specification](../../../superpowers/reports/2026-09-30-reassessment-release-retention-specification.md),
[canonical manifest](../../../superpowers/reports/2026-09-30-reassessment-release-retention-manifest.json)
and [decision receipt](../../../superpowers/reports/2026-09-30-reassessment-release-retention-decision.md)
define the selected closure, exclusions, source locators and safe recovery rules.
The manifest SHA-256 is
`89b12af58a5d8ad547114de429af6009d0b14262153d8945015ed9a99b8c58c6`.
Their checkpoint-specific runtime locators and untracked observations remain
historical statements. Original runtime copies and accounting are preserved.

## Required Git history

The package supplements existing Git providers rather than duplicating them.
Static recovery requires this supplement **and the exact retained Git history**.
A shallow checkout or source-only export is insufficient. All five manifest
provider commits are ancestors of the starting checkpoint
`e795844b441d8e5471494e715f936892f311e0e8`:

- `250da5e66479ee1dd2e7c24cd81905509ffe5969`
- `c321f2e096a71a43bf65787f6f1605c4031266e7`
- `c37c24ee50667121d6b2dc4739aa3b7d12825c96`
- `e795844b441d8e5471494e715f936892f311e0e8`
- `f28de9e900c700d910eb5edf2b0e6f8c336472fe`

The manifest names exact commit/path and nested archive providers. Check their
bytes, not merely the existence of a commit name. The acceptance and harness
commits remain in the same retained ancestry. This is a local availability
claim; no remote publication or remote reference was verified.

## Format and static verification

`OHK-RETENTION-1` has a 32-byte header: 16-byte ASCII magic
`OHK-RETENTION-1` followed by LF, then two unsigned big-endian 64-bit integers:
manifest length (4,154,199) and blob count (3,688). The exact canonical UTF-8
manifest follows; raw blobs follow in ascending SHA-256 order, without padding,
compression or trailer. Manifest offsets and lengths delimit every blob.
The 3,688 unique new blobs contain 72,143,771 bytes; including the manifest,
there are 3,689 logical package members, not that many repository files.

The original receipt retains exact reader/writer source as JSON string
`reader_writer_source` (33,450 bytes, SHA-256
`fc2283db4defc4a39fa9090e7a5259392812f789f75d5849b223aa18a57ad799`),
with `interpretation_instructions`. Read it as data and review it before any
separately authorized use; it is not an automatically executed recovery hook.

For a static check, a trusted reader should stream the committed package blob,
verify both artifact commitments, framing, canonical manifest, unique hashes,
exact offsets/lengths and EOF, and hash every new blob. Resolve required Git
blobs and archive containers from the exact commits; validate every selected
archive member and source-recovery row against the manifest. Reject unsafe
paths, duplicate identities and unexpected lengths. Do not execute archived
code, recreate metadata-only symlinks/special objects, or extract into existing
evidence. See the specification for bounded extraction rules if extraction is
separately authorized.

Repository retention is checked after commit using an independently prepared
data-only reader, against committed bytes and providers, without runtime source
files or full extraction. Its exact source is retained in administrative ledger
record `nr-slice5-qualification-r1/indexes/3602-record.json`; this records the
retention operation, not an additional dependency of the accepted evidence.
The expected closure is 13,238 aliases, 7,195 unique provider-leaf checks,
16 archive providers and 458 source-recovery rows. The final administrative
closeout records the actual committed-byte verification outcome.

## Scope, missing evidence and authority

These bytes support static recovery/inspection of the **manifest-selected**
accepted authority, fixture/oracle amendments, executable/harness provenance,
qualification results and supporting/adverse records. They do not recover all
historical scratch content. Raw output from the disclosed unauthorized probe
remains unrecovered; the disclosure and correction are retained. Missing V1
peak evidence remains missing. No historical result is reconstructed.

Both V1 attempts remain consumed and failed/noncompliant; the retained 19
passing outcomes supplied only the explicitly approved functional exception.
The environment-mismatched control and V2 attempts remain consumed with their
qualification claims withdrawn. The accepted FINAL separately recorded 5,269
passes and 35 expected skips, including all 19 delivery tests. Retention neither
reruns nor retrospectively qualifies any attempt.

Static evidence recovery does not require the old runtime directories.
Application execution/replay is separate: it requires the appropriate historical
source/build, interpreter and dependency identities, supported filesystem,
fresh isolated destinations, accounting and owner authority. Recovered synthetic
authority records are evidence, not permission to authorize a fresh workflow.
The archive supplies neither a portable interpreter nor those new decisions.

Username, absolute runtime/interpreter paths, environment versions, hashes,
synthetic authority and diagnostics are approved for **local Git retention only**.
Publication/external disclosure remain unauthorized; publication readiness is
unestablished. The helper, test-portability and diagnostic corrections remain
deferred. IN-001 and CI-001 remain open and unselected.
