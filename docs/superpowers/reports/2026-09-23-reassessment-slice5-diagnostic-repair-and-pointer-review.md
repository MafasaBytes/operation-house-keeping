# Slice 5 decoder/accounting repair and P10 pointer review

Slice 5 remains incomplete. Two independently authorized repairs are implemented
and verified. The conditional P10 oracle correction is **not applied**: its syntax
is valid, but the required input-field interpretation could not be established.
No additional frozen oracle was changed. Qualification remains paused at this
specific contract ambiguity; final milestone acceptance remains pending.

## Checkpoints and frozen evidence

Starting administrative HEAD `d532effff633e2b8d7a8a8f91d50918e43dbe5e9` and original
tested HEAD `4c68bfc72408f7232259cd32fb05d75eaa68ef2b` were verified.
The unchanged [discrepancy report](2026-09-23-reassessment-slice5-qualification-discrepancy.md)
SHA-256 is `f7fcdd2f93d74fdd2e966297463a4c2015a3e2818fb1ba78ee7b682adddd1476`.
Repair implementation and fresh tested HEAD:
`807d0dc2214b1604d73098f87e2faff533ae06e1`.
The administrative report commit is separately identified in the receipt.

Approved package SHA remains
`454736288217a5c66e8cf6875069aba3a60dee04005c5644d95135adbc8110fb`.
Plan/review, all prior reports and original failures remain unchanged. No new
corpus was created. All work uses the already-approved Slice 5 corpus R.

## P10-fifth: conditional approval check did not establish the field

Read the full packaged CONTRACTS.md and exact frozen case. Section 3, line 122,
requires an ASCII JSON pointer, and says new nr errors name nr Q. The exact
P10-fifth target request is nr.request.v2 SHA
`cc1722b85aabed572220703b491cb5a591af53e053874795065457192fc76fec`.
Its keys are decoder, execution, exposure, id, interpretation, observation,
original_invocation, original_selection_pin, policy, predecessor, procedure,
profile, revision and schema. It has **revision = 5** and a predecessor reference.
It has **no request_chain field**. Therefore `/request_chain` does not resolve
inside this governed request. `request_chain` is the Work/resource-policy dimension,
whose configured ceiling is 4; the request's revision supplies the attempted 5.

The inherited selector CONTRACTS.md section on diagnostics permits a bounded
“JSON-pointer-like semantic path,” including `/required_closure`. Its implementation
also follows procedure references for paths such as `/measurements/0/decoder`.
Thus not every inherited path is a literal pointer through raw request JSON.
However, the reassessment supplement does not explicitly identify a resource-target
projection or say whether `/request_chain` denotes that logical dimension rather
than a request field. The owner's new instruction expressly requires this check.
A leading slash proves syntax, not which governed object it addresses.

The previous report's recommendation was too strong: it established a syntax defect
but did not establish the intended target coordinate. This report corrects that
analysis without rewriting historical bytes. It does not claim the slash correction
is semantically wrong; it reports the missing interpretation required by the
conditional authorization. No runtime output was used to choose a replacement.

Original stderr SHA remains
`6c2adcd0e25bfecd869ca7edbf6230998abac139bbb5cd668750ce92fd07c037` (462 bytes),
with `/target/field` equal to `request_chain`. Expected.json SHA remains
`6521c0eb33a4a6a33f67c02c4e176fb73e67fb3d71c1b0e585f2ef0b31bc4e7c`.
The proposed slash-only stderr digest remains a **non-applied proposal**:
`27b1f83545e3649949f14c94c1a7140622af1b01cfcacf584dd17454db64a642` (463 bytes).
No new oracle commitments exist. Coupled locations remain expected.json
`/diagnostic/path`, cases.json P10-fifth `/expected/diagnostic/path`, and
 diagnostic-catalog.json P10-fifth `/path` (the leading space here is prose only).

Smallest owner decision: explicitly confirm that this resource diagnostic's
`target.field` is the logical dimension path `/request_chain`, with `target.request`
identifying the owning request rather than the JSON object in which the pointer
must resolve. Then the already-proposed slash-only correction can be applied with
mechanically coupled commitments. If a literal request-field pointer is intended,
`/revision` identifies the actual offending field but exceeds the currently approved
slash-only correction and requires explicit direction. Neither option changes
revision identities, attempted/limit values, code, exit or resource policy.

## Three decoder mismatches: repaired independently

For P4-gap, P4-overlap and P4-remote_gap, original public command evidence had
DECODER_INVALID, phase_2, exit 3, but target.field `/original/decoder`, request null
and references empty. Exact frozen diagnostics require `/measurements/0/decoder`,
the owning nm.request.v1 and its exact nominated decoder reference.

Governing CONTRACTS.md section 3 preserves the owning request/reference when
subvalidating nm material, while original decoder integrity occurs in phase 2.
The owning Graph._joins convention supplies the measurement-index/decoder semantic
path; it is not an invented new input schema. The reassessment adapter discarded
those coordinates when catching Graph._decoder errors.

Repair: keep the original decoder validator and phase; map each invalid decoder to
its owning nominated-procedure positions and original request reference; preserve
exact decoder refs and choose by code/path/reference ordering. Resource errors still
propagate immediately. Successful decoder validation and legacy selector code are
unchanged. No frozen P4 expectations were edited.

Fresh red run: **3 failed, 4 passed**, retaining the three missing-coordinate
assertions and four valid/accounting checks. Fresh fixed run at 807d0dc:
**14 passed**, covering all three exact targets, valid partition, original decoder
guards, nearest valid history/context/object boundaries, construction permutation,
and three accounting controls. These are focused checks, not a full suite.

Four actual public CLI reruns at that same HEAD:
- P4-gap: exact frozen diagnostic, exit 3, empty stdout, no publication — passed.
- P4-overlap: exact frozen diagnostic, exit 3, empty stdout, no publication — passed.
- P4-remote_gap: exact frozen diagnostic, exit 3, empty stdout, no publication — passed.
- P4-partition: exit 0, empty stderr and full semantic result excluding runtime
  accounting equal to the mechanically rebound frozen result — passed.

All original red invocations and outputs remain. No broader diagnostic ordering,
full resource matrix, full regression or clean-release pass is inferred.

## Late registration: both bookkeeping and enforcement were affected

The earlier 10,764-byte discrepancy report existed before its external-export
registration. During that interval the census omitted it, and no before-write gate
protected that administrative creation. Thus the failure was **both bookkeeping
and pre-write enforcement**, not merely a delayed label. Its original late record
is preserved; no retrospective continuous-enforcement claim is made.

Fresh starting census reconciled all actual files and registered export bytes:
new 39,827,391; combined 116,387,491; physical 44,617,728 bytes. These included that
report and were below every category and aggregate bound. The plan and earlier
report retain the lapse; no deletion, recategorization or budget increase occurred.

Repair in the test-only evidence driver: publish_export reserves data and index
headroom, appends and fsyncs a charged intent plus its directory **before** exclusive
creation, rechecks the budget, writes/fsyncs the exact bytes, then records completion.
The census includes absent pending intents at their full reserved size; partial or
wrong bytes fail closed. Interruption cannot free that allowance. Existing outputs
cannot be overwritten. This is a single-writer harness, not a production interface
or a concurrency/security guarantee for arbitrary callers bypassing the writer.

Tests establish: denied reservation creates neither export nor intent; at the
instant of exclusive create, the entire payload is already charged; successful
completion charges once and collision preserves bytes; interrupted creation retains
its intent/charge. Test roots are isolated under R/repairs and all artifacts remain.
This report itself is created through the repaired writer, not written first and
registered afterward. Future writers must use the guarded path. This does not
retroactively validate earlier unguarded writes or qualify every future producer.

## Updated qualification and retention

Original matrix accounting remains **35/180 unique commands completed**, 32 passed
the comparisons then performed and three original diagnostic mismatches. Four
fresh reruns do not raise the unique count: they resolve the three mismatches and
refresh the valid twin. There are now 35 unique cases with their performed checks
passing at explicitly different HEADs, **not 35 fully qualified exact matches**.
Original semantic result comparisons excluded runtime accounting. No timeout was
observed in the four reruns. The remaining 145 commands, separate controls, formal
manual dossiers, full regressions and clean-release verification remain pending.

Count four production rerun slots plus two focused test processes conservatively
as **six of sixteen** additional attempt slots consumed, leaving ten. No full-suite
envelope, clean-checkout slot or standalone-recovery-copy slot was used. No unused
Slice 4 capacity transferred. Future reruns must respect these counts.

New repair ZIP_STORED archive at R/exports/diagnostic-accounting-repair-evidence.zip:
1,595,390 bytes; SHA-256
`4c1f2bdf7f1fbf00313c36c024f403410299faab6e21391b956db1ab29d03f71`.
All 349 archive members were compared; symlink metadata is separately represented
in RECOVERY.json. It contains repair material, current logs/indexes and their exact
commitments, not a substitute for the original 20,211,047-byte evidence archive.
No extraction copy or semantic replay was performed for this archive check.
Original archive SHA remains
`91766d1439dc9b457cf0a2bc0a325fb7606e7246b12df860cb6e0c8164998225`.

Before this report and its durable intent/completion records, actual categories:
outputs 10,374,697; inputs 9,150,681; repairs 1,379,540; logs 17,234;
indexes 78,884; exports 21,817,201; regressions/checkouts/recovery zero.
New 42,818,237; combined 119,378,337; physical 48,467,968 bytes.
The receipt supplies the final census including this report and its records.
Approved caps remain new 1,120,927,744; combined 1,197,487,844;
physical reservation 1,204,813,824 bytes. No cap exhaustion occurred.

Preserved: all 3,499 unrelated untracked paths, prior corpora, original package and
oracles, historical reports, dependencies, backend contracts and project ledger.
No physical acquisition, successor work, push, merge or history rewrite. Model-
relative conclusions, exposure limitations, manual adoption and unresolved C remain.

END OF SLICE 5 REPAIR REPORT — P10 TARGET INTERPRETATION REQUIRED.
