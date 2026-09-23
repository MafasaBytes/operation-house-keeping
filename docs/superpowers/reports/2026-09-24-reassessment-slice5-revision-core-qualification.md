# Slice 5 revision-target correction and bounded core qualification

Slice 5 remains incomplete and unaccepted. The P10-fifth targeting correction is
implemented under the owner's explicit `/revision` authorization. No logical
`/request_chain` interpretation, schema amendment, limit increase or ancestry change
was introduced. Qualification resumed; the completed core evidence and subsequent
repairs are below. A demonstrated regression-retention conflict now prevents the
required full-release gate. No full-suite execution was launched into that conflict.

## Checkpoints and exact predicate

Starting administrative HEAD: `19a5ceb183d786a49c4700e76b9c3dd4f433357f`.
Revision-target implementation and 37 resumed core commands:
`f7bf02a8e5b975576db538efc665b1e0d4b02422`.
Owning-request repair and six fresh production commands:
`eb7bd53c3ff8af0736e9ab3f3f0d61d4cbb1d3c2`.
Final focused assertion correction/tested HEAD:
`f66ac30fb95b81b265e10d2115d57d8916241109`.
The administrative commit containing this report/archive is separately identified
in the receipt; it is not a fresh production-command test HEAD.

At the requested starting revision, reassessment_capture.py line 89 calls
`work.high('request_chain',v['revision'])` while entering a captured nr object or
nm request. measurement_wire.py lines 70–72 refuse when `n > self.limits[k]`.
For this fixture the root request's captured **revision is 5**, limit **4**.
It is not the count of traversed ancestors. This check occurs before following
that object's predecessor. The exact offending nr.request.v2 is
`cc1722b85aabed572220703b491cb5a591af53e053874795065457192fc76fec`;
its `/revision` resolves to 5, and it has no `request_chain` field.

The repair catches this guard only when the offending object is the invocation's
request, retains its exact reference, and targets `/revision`. It leaves all guard
values, code, phase, exit 4, ordering and complete-ancestry requirements intact.

## Governing diagnostic definition

Packaged CONTRACTS.md section 3, lines 119–124, says exactly:

> `schema,code,stage,target,resource,retry,bundle_state,message_key`. Target is null
> only in bounded fallback; otherwise exactly `request,field,logical_id,references,
> occurrence_count`. Preserve the owning request/reference when delegating an nm
> error; new nr errors name the nr Q. Field is an ASCII JSON pointer. Resource is
> null or exactly `dimension,attempted,limit`. No unbounded exception text enters a
> stream. `diagnostic-catalog.json` binds expected codes, targets, stages and exits.

The exact wire-catalog.json definition of target.request is an anyOf of
`{"type":"null"}`, a closed reference with kind `nr.request.v2`, and a closed
reference with kind `nm.request.v1`; both references require kind and a 64-lowercase-
hex sha256. target.field is exactly `{"type":"string"}`; the prose further
requires an ASCII JSON pointer. An existing target object cannot have a null field.
The whole target can be null only in the prose's bounded fallback. There is no
separate resource-target variant: resource is null or the closed three-field
object above. Here a known request and captured field are available, so null is
not an appropriate substitute. No schema amendment is necessary.

Exact historical diagnostic (canonical JSON followed by LF):
```json
{"bundle_state":"absent","code":"RESOURCE_LIMIT_EXCEEDED","message_key":"resource_limit_exceeded","resource":{"attempted":5,"dimension":"request_chain","limit":4},"retry":"reduce_input_or_request_policy_review","schema":"nr.diagnostic.v2","stage":"phase_2","target":{"field":"request_chain","logical_id":null,"occurrence_count":null,"references":[],"request":{"kind":"nr.request.v2","sha256":"cc1722b85aabed572220703b491cb5a591af53e053874795065457192fc76fec"}}}
```
Exact corrected diagnostic (canonical JSON followed by LF):
```json
{"bundle_state":"absent","code":"RESOURCE_LIMIT_EXCEEDED","message_key":"resource_limit_exceeded","resource":{"attempted":5,"dimension":"request_chain","limit":4},"retry":"reduce_input_or_request_policy_review","schema":"nr.diagnostic.v2","stage":"phase_2","target":{"field":"/revision","logical_id":null,"occurrence_count":null,"references":[],"request":{"kind":"nr.request.v2","sha256":"cc1722b85aabed572220703b491cb5a591af53e053874795065457192fc76fec"}}}
```

## Frozen correction and recovery commitments

The original package remains SHA-256
`454736288217a5c66e8cf6875069aba3a60dee04005c5644d95135adbc8110fb`.
The active [v2 correction overlay](2026-09-23-reassessment-p10-revision-target-overlay-v2.json)
SHA-256 is `1612a1cf826bde32d6a4c161b030bc95d18e1f325781c27d55249642059e0328`.
It retains exact byte replacements, old/new sizes and full hashes for four members:

| Member | Changed pointer | Old SHA-256 | New SHA-256 |
|---|---|---|---|
| cases/P10-fifth/stderr.expected | /target/field | 6c2adcd0e25bfecd869ca7edbf6230998abac139bbb5cd668750ce92fd07c037 | 94bba821db29c523bf7730d16bbe6cb131d24e36fbcf56fa6072950a94cbe728 |
| cases/P10-fifth/expected.json | /diagnostic/path | 6521c0eb33a4a6a33f67c02c4e176fb73e67fb3d71c1b0e585f2ef0b31bc4e7c | d70c811ef08a0ac0c97bcc61f09330eea4ac85a43600754f8ec0280bc02aa1ad |
| cases.json | /49/expected/diagnostic/path | 13e49c8b64e30a8a0f4b9bdf59f18dcdfe82e24ff471093e37413c9b5c8dd153 | b8b5cd467bf447c536fa04a587215f3feb66223908c47fa6ddc0b137e7641e6b |
| diagnostic-catalog.json | /core/12/path | 9ac06ac1b6d72723e734496841b23b95630144b87f9203214e48af6da3ebeffd | 50b6e75f9c60427fd27584fc81a846dc0c4bc1371520d1ca8f7253d7773e9837 |

Only `request_chain` becomes `/revision`; all surrounding bytes are preserved.
The initial overlay erroneously calculated a canonicalized cases.json commitment;
it was never used for a corrected runtime oracle. Its bytes remain preserved and
explicitly superseded by v2. No request, revision identity, code, exit, resource
value or other semantic expectation was changed.

Historical reports remain byte-identical:
- [Original discrepancy](2026-09-23-reassessment-slice5-qualification-discrepancy.md):
  `f7fcdd2f93d74fdd2e966297463a4c2015a3e2818fb1ba78ee7b682adddd1476`.
- [Prior diagnostic/accounting report](2026-09-23-reassessment-slice5-diagnostic-repair-and-pointer-review.md):
  `4c46019abf87e80643664382341ec6726b4317e5c48a7c4dd85fbb9b1246b609`.
Its proposed `/request_chain` owner question is superseded by this inspected
predicate and the owner's `/revision` instruction, not silently rewritten.

## Verification and remaining comparison limits

The revision assertion was red before repair; the fixed focused selection passed
4 tests. Real production P10-shared_four completed and P10-fifth refused with the
exact corrected diagnostic at f7bf02a. Both were first executions of their matrix
entries. No five-revision material was admitted or truncated.

All **72 unique core evaluations** have now executed: 35 at 4c68bfc and 37 at
f7bf02a. Original results include three decoder failures and five later request-
reference failures. Four prior public decoder twins passed at 807d0dc; six new
public commands at eb7bd53 cover five repaired refusals and valid P10-context8.
Thus 82 total production invocations are retained: 72 matrix entries plus 10
repair/valid-twin reruns, zero timeouts. Latest case comparisons are passing for
72/72, spread across those exact HEADs, **not a final-candidate 180/180 result**.

The five new ordinary implementation omissions were:

| Case | Preserved code / phase / field | Required owner |
|---|---|---|
| P9-context | SUPPORT_SUBJECT_MISMATCH / phase_3 / /context/evidence | original nm Q |
| P10b-external | AUTHORITY_PIN_REQUIRED / phase_1 / /authority_pin | nr Q |
| P10-rational129 | RESOURCE_LIMIT_EXCEEDED / phase_3 / /observation/scalar | nr Q |
| P10-context9 | RESOURCE_LIMIT_EXCEEDED / phase_2 / /request_contexts | nr Q |
| P10-objects129 | RESOURCE_LIMIT_EXCEEDED / phase_2 / /unique_objects | nr Q |

Before repair each request was null. After repair every complete diagnostic byte
matches its frozen oracle; stdout stays empty, no bundle exists, exits are 3 for
the first two and 4 for the resource refusals. No oracle edits were made for these.
The adapter now preserves the owning original request on delegated joins and the
known nr request on authority/capture/numeric refusals. Legacy validators unchanged.

The one-off repair comparator mistakenly used exit 2; its failed comparison records
remain. A separate append-only correction compares the retained actual statuses
against command-matrix.json's 3/4 expectations. No command rerun or oracle change
was needed. Focused tests initially had 14 passed / 2 failed because they compared
internal bare resource dimensions with public formatted fields. The test-only
correction checks internal owner/code/phase; public twins check exact emitted bytes.
Final focused run: **16 passed in 3.78s at f66ac30**; original failure log preserved.

Core success comparisons establish semantic result equality excluding measured
accounting, bound trace equality and canonical receipt/hash consistency. They do
not yet establish independent expected physical accounting or the entire delivery,
stream/fault and resource matrix. The remaining **108** commands (20 verification,
20 replay, 28 delivery, 40 resource), ten separate internal/fault controls, 24 guard
pairs, three manual dossiers, full regressions and final clean release gates remain
pending. Prior evidence is not promoted to final-build verification. f66ac30 changes
only test assertions from eb7bd53, but its build commitment differs; no same-build
replay claim is inferred from unchanged production source.

## Accounting repair, measured usage and custody

Prior late export registration affected both bookkeeping and pre-write enforcement.
The historical failure is retained. The fixed export path reserves before creating
anything, writes/fsyncs a charged intent, exclusively publishes exact bytes, and
records completion. An interrupted intent remains charged; unexpected bytes fail
closed. Current exports use that path. There is no claim of retrospectively
continuous enforcement for the original defective write.

All 16 conservatively allocated additional attempt slots are now used: four prior
production decoder runs plus two focused processes; revision red/fixed processes;
six owning-request production twins; owning-request failed/fixed focused processes.
No slot was recycled or deleted. New calibration/reruns require an explicit finite
plan correction; unused byte capacity alone is not rerun authority.

Measured executable witnesses are 27,632 bytes; this is not a frozen future size.
The eb7bd53 witness SHA is
`ee59e275e42cbe50774c14c1550a1cb12b308323804acb01ca9a195b5a900d03`;
a read-only f66ac30 producer check is
`4c5ab327b003fe20e93f3aea6dcabff496111c7e0994eb94535f8c52d067358c`.
Largest completed core bundle: P7-newbaseline, 523,840 bytes; closure 479,864,
result 7,333 and trace 6,589. Per-case raw accounting is retained; these corpus
observations are not general runtime-capacity guarantees.

[Recovery archive](2026-09-24-reassessment-slice5-core-correction-evidence.zip):
43,575,847 bytes, SHA-256
`646cf92d296d87ba1f661f7c295aee0f27eeedca6f86e0982d2659c7bcf7c7a4`.
3,655 members recover the current raw corpus snapshot excluding already exported
archives: exact inputs, outputs, repairs, original failures, logs, identity and
indexes plus RECOVERY-MANIFEST.json. Every listed member was read back and checked
for exact size/hash in memory. No extra extraction copy was made. Earlier exports,
committed package and overlay remain separate recovery references; hashes alone
are not offered as missing content. Source evidence and this archive both count.

Snapshot after archive publication, before this separately charged report:

| Category | Bytes |
|---|---:|
| outputs | 19,646,652 |
| inputs | 18,762,363 |
| repairs | 3,309,000 |
| regressions / checkouts / recovery | 0 / 0 / 0 |
| logs | 36,112 |
| indexes | 180,635 |
| exports, including registered external files | 65,408,313 |
| new total | 107,343,075 |
| combined with frozen H+Q | 183,903,175 |
| allocated physical bytes | 120,401,920 |

3,675 files / 365 directories. All are below unchanged approved category/new/
combined/physical ceilings. Final receipt provides the post-report census; its
intent/completion indexes are necessarily newer than this archive snapshot.

## Concrete remaining retention blocker and smallest next decision

The plan's “Full-suite/application-gate artifacts” category includes test scratch
and permits two 64-MiB envelopes: 134,217,728 bytes total. Categories cannot borrow.
“Clean committed checkouts and metadata” permits two 256-MiB slots, the second only
as a repair contingency. The plan expressly requires stopping if full-suite storage
cannot be conservatively reserved. This is not a per-directory reset.

Required existing test_s7_release.py lines 26–30 uses local
`git clone --quiet --no-hardlinks`. Its test at lines 54–55 creates two independent
current clones simultaneously; another test at line 125 creates a historical clone.
Pre-export read-only sizing at f66ac30: current tracked tree 230,878,480 bytes;
.git/objects regular content 162,586,657 bytes. Two current working trees alone
require 461,756,960 bytes, exceeding the entire regression category by 327,539,232.
A local --no-hardlinks clone's tree plus copied object payload is at least
393,465,137 bytes, exceeding one 268,435,456-byte clean slot by 125,029,681; two
exceed the 536,870,912-byte checkout category by 250,059,362. Git metadata, third
historical clone, test outputs and later committed evidence add further demand.
These are measured lower bounds before this new archive/report, not an asserted
full-suite maximum. No clone/test was launched. No logical sharing/compression
savings, alternate category allocation or unretained temporary cleanup is assumed.

Smallest next owner action: authorize a bounded retention/execution-plan correction
that measures the actual required regression clone schedule and specifies any
permitted clone-carriage adaptation, category allocation and finite additional
calibration/repair attempts. Approve its exact revised accounting before execution.
No production semantic/resource limit increase is implied. The existing test path
cannot fit the approved categories; this report does not claim every alternative
representation is impossible. It does not propose an arbitrary new cap or silently
borrow unused allocations. All current category limits remain effective.

## Preservation and gate

Tracked modifications are limited to diagnostic adapters, focused tests, test-only
qualification oracle loading, two explicit historical/active overlays and this
report/archive. All 3,499 pre-existing untracked paths remain; no bulk staging,
cleanup, parent-corpus write, dependency/backend/ledger edit or remote operation.
Frozen package and report hashes above were freshly verified. Parent H/Q remain
in place; no new claim of rehashing every parent file is made. Same-author oracle
provenance, model-relative conclusions, local exposure declarations and manual
adoption are unchanged. Slice 5 and final milestone acceptance remain pending.

END OF REVISION CORRECTION AND BOUNDED CORE QUALIFICATION REPORT.
