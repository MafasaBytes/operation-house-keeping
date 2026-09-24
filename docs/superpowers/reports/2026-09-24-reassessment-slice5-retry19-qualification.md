# Reassessment Slice 5 — 19 named retries and current-candidate evidence

All 19 authorized retries passed at one candidate. All 53 unused planned core
refreshes also passed there: **72/72 core cases, exact semantic/trace or refusal
comparisons, zero timeouts**. Slice 5 and final release remain unqualified.
A resource calibration fixture failed; it was not a production regression and
has not been retried. No new repair contingency or byte allowance was consumed.

## Authority and exact heads

- Starting administrative HEAD: `1e191b7a91dc63420858f8debf7d4543ff0d17e7`.
- Previous repaired executable: `af86f93929b7fcb161fc4a8466a02e6f02372a80`.
- Prior report verified unchanged, SHA-256:
  `6fc6245330d8aa7c27935835c6891a7d3f2a5982db34f824f7b9127e0833d052`.
- Separate owner-approval commit and **single tested candidate**:
  `40fbb7b0a5ea5251179a9661c782a41cf7356ed6`.
  Its applications/backend trees equal the repaired executable's trees. The only
  intervening change was documentation. Its actual build was freshly derived and
  bound; the old build witness was not passed off as the new one.
- This report's administrative commit is the commit introducing this report,
  evidence and test-only drivers. Its hash is returned separately. It is not a
  newly tested executable checkpoint. No production source changed this turn.

[Approval](2026-09-24-reassessment-slice5-retry19-owner-approval.md) SHA-256:
`0ef427adf1c4d60ba0ed2b38495921e3135dd3c1c51e06ca143a8d0f1a72a861`.
[Pre-execution schedule](2026-09-24-reassessment-slice5-retry19-schedule.json)
SHA-256 `64502eae14d5799d8fa56ede638f2ad60a52b5ffe92ca199d49fce43c2f2ed42`.
The schedule identifies each original attempt/outcome, reason, named case, target
HEAD, bound invocation, expected result/trace/refusal commitments and per-slot
allowance. It was retained before execution, not reconstructed from passing results.
The 19th old refresh consumed its operational slot but was interrupted before
application launch; it supplies no application-execution evidence.

Fresh approved-executor probing wrote/fsynced/read and removed only its uniquely
named six-byte probe at the existing ext4 corpus. No permissions, mounts, ownership
or security settings changed. Safe paths, clean executable trees, actual build
identity and durable category reservations were checked before launches. Existing
passing channel twins at af86f93 were reused through executable-tree comparison;
no retry was spent repeating them.

## Actual qualification and limits of the comparisons

[Evidence matrix](2026-09-24-reassessment-slice5-retry19-matrix.json), 506,293 bytes,
SHA-256 `402e2a5cf3da846e8af2ac2e424a0e04fb618317200e6eb81a7024f60464b5f4`,
records all 180 identities, actual argv/heads/outcomes, listed checks, history,
pending commands, slot counts and per-case runtime measurements.

| Group | Evidence at the tested candidate | Other status |
| --- | --- | --- |
| 72 core E | 72 matched; 19 named retries +53 unused planned refreshes | Original attempts preserved, not substituted |
| 20 V | 20 matched exact canonical receipts, exits and streams | Verification is not semantic recomputation |
| 20 R | 20 matched receipts/exits/streams and all six recovered semantic files | Real CLI semantic recomputation; clean-checkout/access-isolation gate still pending |
| 28 D | Five remaining cases passed their listed checks | 23 have historical-head evidence only; not counted as current-candidate passes |
| 40 B | 38 matched; one failed calibration fixture | One not launched; manifest pair remains incomplete |

Thus **156 matrix-command attempts at 40fbb7b: 155 matched their defined checks,
one failed, zero timeouts**. Across historical and current execution, 179 distinct
matrix identities have been launched; this is not 179 passes or a 180-command
final-candidate qualification. Historical D evidence still needs explicit
executed-path equivalence justification or separately authorized refreshes. It is
not silently combined with current passes.

Core successful comparisons cover the frozen semantic result (excluding observed
runtime accounting), exact mechanically build-bound trace, exact receipt after
actual manifest-hash binding, complete bundle size and canonical channels. Core
refusals compare exact frozen diagnostic bytes, empty stdout, exit and no bundle.
Frozen outputs never entered production computation. The original same-author
hand oracle and separate same-author static check remain comparison provenance,
not independent reviewer evidence.

Five new D checks establish public identity collision, extra closure rejection,
forged-result integrity acceptance followed by semantic replay rejection, and
incomplete-bundle refusal. The forged bundle changes conclusions and is
self-consistently rehashed; replay derives its own result and rejects it. Stored
byte verification alone does not establish correct conclusions. D comparisons
check code/exit/canonical streams/publication state; they do not discharge every
exact target/stage/ordering obligation merely because those checks pass.

All 24 separately allocated internal policy guard pairs passed: actual Work.high
at N, refusal at N+1, original counter unchanged after refusal. They are internal
algorithm evidence, not public maximum-sized inputs or a claim that simultaneous
policy maxima fit. Two internal capture/compute calibration passes recorded actual
guard demand without publication; no supplied expected conclusion was computed
by an oracle callback. Three manual dossiers record C unresolved, chronology as
local declaration rather than custody proof, and derived reporting/manual adoption.
These do not count toward 180 application commands. Prior cycle/channel evidence
retains its original heads. Six remaining fault/race/ordering controls are pending.

## Classified failure — no unauthorized retry

`B-manifest_bytes-fit` expected completed exit 0. It emitted exit 4, empty stdout
and canonical RESOURCE_LIMIT_EXCEEDED; resource was
`{"attempted":972,"dimension":"manifest_bytes","limit":971}`,
stage phase_2, bundle_state absent. No output directory was published.

**Classification: test-fixture calibration defect.** The observational guard pass
had covered required prior-file recovery, but qualification_resources.py replaced
that whole-path manifest maximum with the new seed bundle's 971-byte manifest.
The required original nm.bundle.v1 manifest is **972 bytes**, commitment
`8d88a43b5536326fb6020947ba8afe56fd59abace501be06fdd9b75ce6d86239`.
In reassessment_capture.py `_recover`, each original retained file executes
`effective.guard(CAPS[name], len(raw))` before decoding/role interpretation. The
972-byte original manifest therefore correctly refused at limit 971, before new
publication. This is not evidence of a failed product fit at the true demand.
RESOURCES.md requires demand including reservations and prior reconstruction;
output length alone is not the resource demand.

The exact failed driver, limit file, stdout/stderr, command/result, calibration
record and failure comparisons remain in the corpus and recovery archive. The
harness now takes max(observed whole-path demand, new seed manifest size), leaving
production, limits, requests, diagnostic code and frozen expectations unchanged.
That static correction is **not** a passing rerun. Fresh output physical metadata
can vary in length, so a corrected schedule must account for the full path and
cannot assume a universally fixed manifest size from one seed.

No B-manifest_bytes-fit retry was launched. B-manifest_bytes-below also remains
unused. The remaining 16 unrelated original B commands were checked unused before
launch and all passed; they were not relabelled repairs. Their fit checks preserve
semantic result/trace; refusals check dimension, attempted value, limit, streams
and no successful publication. Earlier unavoidable guards can constrain which
boundary is actually observed; these are not generic public-maximum proofs.

**Smallest additional attempt decision:** one named B-manifest_bytes-fit retry,
only after correcting and retaining its full-path calibration schedule, under the
existing per-attempt/category/aggregate ceilings. This is not granted by this
report. Its existing below-limit partner remains an unused original command.
No general retry pool or additional repair contingency is requested. Full-suite,
remaining controls and clean-delivery obligations retain existing authority but
are not passes, nor are they newly gated on permission simply for being unfinished.

## Slots and retained work

| Allocation | Consumed | Remaining |
| --- | ---: | ---: |
| Historical repair attempts | 16 | 0 |
| Additional repair contingencies | 16 | 0 |
| Original planned core refresh slots | 72 | 0 |
| Newly authorized case-specific retries | 19 | 0 |
| Original resource commands | 39 | 1 |
| Original verification / replay commands | 20 /20 | 0 /0 |
| Original D delivery commands | 28 | 0 |

The original 72 refreshes include 18 earlier-head passes, one interrupted
pre-launch attempt and 53 current runs. Adding the 19 named retries yields 72
current-candidate results without erasing 19 consumed old slots. Allocation rows
are not a count of all application executions. Full regression envelopes, the
three approved checkout slots and four recovery-copy slots remain unused. Neither
unused bytes nor a failed comparison replenishes an attempt allowance.

Measured completed-core maxima: build **27,632** bytes; captured input **354,668**;
closure **479,864**; complete seven-file bundle **523,840** (P7-newbaseline).
Largest result 7,333; trace 14,445; original reconstructed prior bundle 232,849.
The largest complete bundle remains below 1 MiB and closure below 524,288.
Recorded per-case manifest maxima include 48,107,771 bytes read, 2,498 read calls,
522,869 bytes written/six writes before manifest write, 3,415,154,784 ns and
91,836,416-byte process peak RSS. These maxima can come from different cases;
they are observations, not guarantees or summed independent peaks. Manifest
physical fields explicitly exclude its own later write. Internal calibration
also records hashing, decoding, reconstruction and contextual work separately.

Census after matrix/archive publication, before this report's own charged export:

| Category | Bytes | Cap |
| --- | ---: | ---: |
| outputs | 35,998,310 | 103,809,024 |
| inputs | 27,366,908 | 71,303,168 |
| repairs | 54,402,518 | 188,743,680 |
| regressions | 0 | 134,217,728 |
| checkouts | 0 | 620,756,992 |
| recovery | 0 | 4,194,304 |
| logs | 112,507 | 8,388,608 |
| indexes | 1,076,656 | 8,388,608 |
| exports | 72,701,222 | 134,217,728 |
| new total | **191,658,121** | **1,274,019,840** |
| combined H+Q+new | **268,218,221** | **1,350,579,940** |

Observed new allocated bytes227,422,208 of1,441,792,000; 10,454 files/829 directories
of32,768/4,096. The final receipt records the post-report census. These are observed
snapshots, not a continuous measured physical peak. Durable reservations precede
this turn's bounded producers; previous late-registration/directory-estimation
failures remain disclosed, not retroactively declared continuously enforced.
There are no pending interrupted reservations from this turn. No deletion,
replacement corpus, category transfer, cap increase or uncounted clone occurred.

## Recovery, preservation and remaining release gates

[Selected recovery archive](2026-09-24-reassessment-slice5-retry19-evidence.zip):
1,397,026 bytes, SHA-256
`c1fc61dd08b247b01eb4eae2e92139dc20389dc9633a32d83abd87e6be220c11`.
All1,341 entries (5,048,381 decoded bytes) were recovered in memory and compared
byte-for-byte. It contains this turn's command streams/index records, exact
schedule/matrix/drivers including the failed driver, four complete representative
bundles and an exact member index for all retained R files. It does **not** claim
to archive every raw input copy: those bytes remain in R, identified explicitly.
Hashes alone are not substitute recovery bytes. Symlinks/FIFO are inert metadata
in the export, never traversed or silently recreated. Recovery checking was static,
not an additional application proof or clean-environment replay.

Fresh preservation checks: all3,499 unrelated untracked paths match their earlier
byte inventory; all3,654 core-correction and2,782 resumed archive payload members
still match live R. H remains1,951 regular files/65,433,988 bytes and reproduces
canonical triple-array SHA-256
`0ae693f44e5ca9edf0ab94e9958a436ab32e74a12d43c09703c171c89d62dd14`.
Q remains11,126,112 bytes, including exports. No frozen report, package, oracle,
original failure, ledger, dependency, backend or old runtime result was changed.
Only named new evidence and test-only drivers are to be staged; no bulk staging.

Remaining: incomplete manifest boundary pair; historical-only D attribution audit;
exact outstanding diagnostics/order and six fault/race controls; full repository
regressions and required application gates; approved three-root materialization,
clean committed-input delivery/recomputation and final release documentation.
The full-suite delivery helper still targets historical Q and must be adapted to
R with explicit accounting before running; clone subtrees and full-suite write
demand need preflight. No selective checkout or core count substitutes for that
suite. No clone, full-suite run or final clean-delivery claim is made here.

Local attestation is not authenticated identity or exposure custody. Conclusions
remain model-relative, full-envelope, derived and manually adopted. No pruning,
automatic reranking, physical execution, probability or causal-validity claim.
C remains unresolved; IN-001/CI-001 remain open and unselected. No successor work,
dependency acquisition, backend extension, remote operation or history rewrite.

Final milestone acceptance remains pending.
