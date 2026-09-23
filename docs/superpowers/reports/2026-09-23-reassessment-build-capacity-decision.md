# Reassessment build-capacity decision

**Verdict: package ready under the existing contract, for this bounded capacity
question. No carriage, limit or supported-input amendment is required.** This is
not package approval, a freeze, implementation authorization or runtime qualification.
The required completed cases are realistically supportable; the actual future build
must still fit after complete binding and accounting. A failed required valid case
cannot be converted into an expected refusal merely to obtain qualification.

## 1. Verified authority and meaning of the ceiling

Checkpoint: `15bd9dcb1559898944149cab0ec78b962019ab50`. Verified unchanged inputs:

| Artifact in `2026-09-23-reassessment-preparation/` | SHA-256 |
| --- | --- |
| READINESS.md | `e182d6da8ffb505402cf65fd277ed5b1148390e4676eb902cbe8b5fcaa91829d` |
| package.zip | `454736288217a5c66e8cf6875069aba3a60dee04005c5644d95135adbc8110fb` |
| MANIFEST.json | `3a7c1d176c2231e8b9b938e404b2500e32eb87bfd12cdf046f144d0953edf0cf` |
| recovery-receipt.json | `e92e024e69987ad900300976d3f3dbd337af68697a115fe732b29f345e3c301c` |

The **65,536-byte build allowance is an independently enforced admission ceiling**,
not an assurance that every otherwise valid build of that size fits every request.
It is not an unmeasured placeholder. The *prepared witness* and *runtime feasibility*
are different matters; neither changes the meaning of the approved numerical ceiling.

The governing selector [RESOURCES.md, accounting paragraph 6](2026-09-19-next-measurement-preparation/RESOURCES.md)
(line 41, SHA `61918e1b11e101dce6f4cf3c745dcc32dfb58ff35768ba00fc8031eb1e4b5263`)
explicitly says: “Per-component limits do not guarantee that arbitrary simultaneous
maxima fit: the aggregate guard wins.” Its line 32 makes the history envelope
subject to every other guard. These bytes also match the exact manifest-bound
archive retained in the reassessment package. Their original pending-policy wording
is historical: the owner subsequently approved that exact selector resource policy.

The approved [v2 amendment §4](2026-09-23-reassessment-prior-bundle-carriage-amendment.md)
retains those ceilings, separately charges reconstructed original files and full new
delivery, and requires duplicate inspection copies and manifest reserve to count.
The approved [reassessment candidate §8](2026-09-23-measurement-result-reassessment-corrected-candidate.md)
requires combined feasibility without inventing capacity. The pending package's
[CONTRACTS §§4–6](2026-09-23-reassessment-preparation/CONTRACTS.md) and
[RESOURCES, “Measured fit”](2026-09-23-reassessment-preparation/RESOURCES.md)
apply that existing conjunction. They do not create a promise of Cartesian-product
capacity. All narrower public-input, object, work and numerical guards remain.

## 2. Actual maintained witness and charges

Invoked the existing read-only `measurement_build.identity(work)` producer once,
with its existing `Work()` instrumentation, under
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python`
using `-B` and `PYTHONDONTWRITEBYTECODE=1`. No evaluate, verify, replay, reassessment
command or test was run. The producer retains its clean-source/interpreter/lock
checks; no identity field, source list, dependency or guard was overridden.

| Observed producer quantity | Exact value |
| --- | ---: |
| Complete canonical `nm.build.v1` bytes | 26,165 |
| Source/lock manifest entries | 164 |
| Source/lock content hashed | 1,888,614 bytes |
| Installed distributions / non-pyc artifact entries | 10 / 652 |
| Distribution content hashed | 13,757,356 bytes |
| Interpreter content hashed | 32,003,680 bytes |
| Additional lock read (also in source manifest) | 191 bytes |
| Producer `build_bytes_read` / `build_read_operations` | 47,649,841 / 2,199 |
| Producer elapsed wall time | 3,317,291,299 ns |

The witness SHA is `731866497843126d265da8afb59c00a88df83a39dd27d984da554d0b13870339`.
Environment: CPython 3.13.11, Linux x86_64, glibc 2.39. The counters count the
producer's instrumented hashing reads, including EOF read attempts and the repeated
lock read. They exclude imports, Git/metadata discovery I/O and the audit's temporary
output write; they are not a complete OS-work measurement or a future command budget.
No reassessment CPU/RSS, capture, reconstruction or publication was measured.

Exact audit recovery is possible from the frozen historical 26,165-byte witness
`870ad9750fbef990a54180c2e10a7d4884b723d2c82dd9f2f9e188cec637ac7a` in the package:
these were the **only** differing JSON values; replace them and canonically serialize.

| JSON pointer | Current value |
| --- | --- |
| `/checkpoint` | `15bd9dcb1559898944149cab0ec78b962019ab50` |
| `/environment_manifest/distributions/0/artifact_manifest_sha256` (Pygments) | `21897358b6b89fb7c77d3a15b20a993f52d545849a9628c23070ca00191b60b3` |
| `/environment_manifest/distributions/7/artifact_manifest_sha256` (pytest) | `123852c3b1d63e2fe28b1440aac1dea8eb9e0d116de5310fcbf87c3bb219a431` |

Verify the reconstructed size/SHA above. This audit reconstruction is not a proposed
production delta format. Equal witness sizes do not imply equal executable identities;
the historical witness is unchanged. No claim of historical same-build replay follows.

Carriage and work are distinct:

* New build B: one complete typed object in unique capture; one base64 copy of length
  `4*ceil(B/3)` in new closure; one exact raw B-byte `build.json` inspection copy.
  Its identity references are checked at every required use. Live source/dependency
  hashing derives the actual witness independently; comparison cannot trust the input.
* Historical build: one separate immutable 26,165-byte object, encoded once as 34,888
  bytes in new closure. It cannot alias the distinct new nr build. P7-newbaseline
  includes this object but no optional prior-bundle descriptor.
* When an original bundle is supplied, the v2 recipe reuses that historical object.
  It reconstructs its original raw build file and its encoded occurrence in the
  original closure. Their 26,165 + 34,888 bytes remain part of the 232,849-byte original
  reconstruction work. Original file-role, reference and manifest checks still run.
* Standalone replay reads both new retained representations, decodes captured objects,
  verifies equality, reconstructs any original bundle and derives the actual live
  build again. Charge every actual read, decode, hash, role/context check and copy.
  Unique storage is not a refund of work; physical call counts remain implementation-
  and execution-dependent and must be measured, not inferred from copy counts.

The repeated external new `build.json` is deliberately required by the seven-file
contract (selector CONTRACTS line 59). Removing it would change the delivery contract
and would **not** reduce closure size. Sharing source-manifest substructure between
two different whole witnesses would need another versioned reconstruction contract.
Neither change is necessary. The approved v2 recipe already removes duplicate
carriage of the *original closure* without removing its reconstruction obligations.

## 3. Exact capacity arithmetic and realistic growth

Re-read all 51 completed-case measurements without regenerating any fixture.
P7-newbaseline is the binding closure: the next-tightest completed case would allow
130,764 build bytes by closure arithmetic alone, before the independent 65,536 cap.

P7's seven file sizes are invocation **575**, closure **478,220**, result **7,333**,
trace **6,589**, prepared build **26,398**, policy **876**, static manifest **947**:
sum **520,938**. Closure framing is **6,928** bytes; encoded member content is
**471,292**, including **35,200** for the new prepared build. Thus, with the other
case bytes fixed:

```text
closure(B) = 443020 + 4*ceil(B/3)
capture(B) = 327036 + B
bundle(B,M) = 15373 + closure(B) + B + M
publication_reserve(B) = bundle(B,16384)
```

The fixed 15,373 is invocation + result + trace + policy, not omitted evidence.
M is the actual fresh physical-work manifest. Its static 947-byte template has
null counters and is not runtime evidence. The full 16,384-byte reservation covers
its permitted size; actual growth must be bounded during construction. For example,
billions of hashing input bytes become numerical counters, not billions of retained
bytes. Detailed work logs are separate qualification evidence, never an excuse to
drop manifest fields. Real binding must recalculate logical counter digit lengths,
result/trace bytes and every commitment; the fixed-byte equations are explicit
sensitivity calculations, not a claim that arbitrary rebinding changes nothing else.

| B: size scenario, not substituted package bytes | Closure | Bundle with static M=947 | Full manifest reservation |
| --- | ---: | ---: | ---: |
| 26,165: current actual nm size, wrong profile for future nr | 477,908 | 520,393 | 535,830 |
| 26,318: nr field-shape projection of complete current manifest | 478,112 | 520,750 | 536,187 |
| 26,398: unchanged package specimen | 478,220 | 520,938 | 536,375 |
| 30,646: explicitly conditional planning sensitivity below | 483,884 | 530,850 | 546,287 |
| 60,951: fixed-case closure boundary | 524,288 | 601,559 | 616,996 |
| 60,952: first failing B | 524,292 | 601,564 | 617,001 |
| 65,536: independent build ceiling | 530,404 | 612,260 | 627,697 |

At 65,536, closure exceeds its 524,288 ceiling by **6,116**; capture is 392,572
and bundle reservation remains below 1,048,576. The closure guard must refuse.
This is allowed aggregate exhaustion, not a demonstrated contract contradiction.
60,951 is a property of this fixed fixture, not a new supported-build policy.

The complete current source/environment inventory is used for the 26,318-byte
shape projection: add predecessor and supported-nm-contract fields, use the nr
schema/profile and 64-character body-derived ID. Contract digest remains 64 characters.
The 153-byte difference is grammar overhead, **not** a produced nr executable identity.
The existing larger 26,398-byte specimen remains untouched; no smaller witness was
selected or bound to make a case pass.

Current source-entry serialization is 117–175 bytes including its comma, mean
145.14. The maintained selector/support implementation occupies ten manifest entries
(1,621 serialized bytes). The proposed application-only five-slice plan reuses those
facilities and adds no dependencies/backend layer. A transparent planning sensitivity
allows **20 additional entries at 200 bytes each**, plus **two additional file-size
digits for each of 164 existing entries**: `26318 + 4000 + 328 = 30646`. This leaves
40,404 closure bytes and 30,305 raw-build bytes before the fixed-case boundary.
The entry-count/path/digit assumptions are an engineering estimate, not new limits,
a promised layout or a guaranteed upper bound. Larger source contents primarily
increase hashing work; a fixed-width digest does not embed the source bytes. Even
this twice-the-current-module-count sensitivity is comfortably below the boundary,
supporting realistic feasibility without claiming future runtime capacity.

All independent output maxima, if their closure has first passed, reserve
`16384 + 524288 + 65536 + 131072 + 65536 + 876 + 16384 = 820076` bytes, below
the 1 MiB bundle ceiling. Successful stdout separately reserves 1,024 bytes (core
maximum 312; P7 288). Refusal stderr separately reserves 2,048 (core maximum 704),
with empty stdout; it is not a partial successful bundle. These streams are counted
as output work under their own guards, not concealed in or deducted from closure.
There is no guarantee that every independently bounded input reaches publication.

## 4. Smallest owner decision and preservation

**Accept the capacity interpretation: independent ceilings plus aggregate refusal
already govern; no amendment is needed to proceed to exact-package review.** Keep
all required valid cases. Before any future implementation is accepted, derive the
complete actual nr build, mechanically bind it, recalculate all case accounting,
and demonstrate every required valid case fits and all adverse boundaries refuse.
Measure physical work and runtime limits separately. If that actual required build
fails, stop then for one explicit owner decision; do not truncate evidence, omit
source entries, weaken lower-layer guards, silently restrict inputs or relabel a
valid case. Exact-package/accounting-policy approval and implementation remain
separate gates. This report neither freezes nor regenerates the 72-case package.

Starting inventory: **4,755 regular tracked/untracked files, 3,501 untracked paths**.
Only this report is added. Historical package/report/witness bytes and the unresolved
review-digest discrepancy remain unchanged. No code, tests, application commands,
dependencies, limits, ledger, Git commits or remote operations were introduced.
Temporary sizing outputs are audit material, not runtime results or production input.

END OF REASSESSMENT BUILD-CAPACITY DECISION.
