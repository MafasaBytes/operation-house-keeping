# EA-001 Slice A Integrity Repair Completion Report

Date: 2026-09-05

Status: repair continuation complete at the tested implementation commit;
owner validation pending; EA-001 Slices B and C remain unauthorized

## 1. Authority, boundary, and tested result

The continuation handoff authorized only the existing DS-004 operational-
evidence reader repair. The starting branch and HEAD were exactly `ea001` and
`dd287135e3142207dc6655cbd36a81471b48f68d`. The only starting working-tree
entry was this untracked completion report at 3,430 UTF-8 bytes and SHA-256
`571adbb41ccf5a152eb1acdd0244889e5b68d504a4809ab822dfbb3c9db88033`.

The bounded continuation is implemented and tested at:

`ceee1446f18ae9b7134005089046a5a4d69e10ae`

Production remains confined to
`backend/data_sources/evidence/operational_api.py`. No
`backend/evidence_assurance` package, temporal behavior, schema, projector,
public field, export, error vocabulary, production limit, source fixture,
model record, ledger record, or canonical artifact was added or changed.

## 2. Accepted inputs and complete commit lineage

All required inputs were read completely. Their accepted digests matched:

| Input | SHA-256 |
| --- | --- |
| Corrected EA synthesis | `557b2df9aec5ee784006bfdba771936ae90844ea7cf8913c1e61455fa4a7e08e` |
| Slice B contract-correction report | `43b205758cf3903132b5ac56a90f6536183f84cb6c92c967355c8972518ec1b1` |
| Corrected Slice B plan | `419e25c6cc752356292fdaeb98d635b01140d718f0aff2271379665a7fb93bd5` |
| Preliminary repair report | `571adbb41ccf5a152eb1acdd0244889e5b68d504a4809ab822dfbb3c9db88033` |

The complete ordinary forward commit chain after the accepted discrepancy stop
is:

1. `490b4ebe0aa3f7929b4432992b50769a75ae6c26` — accept contract correction.
2. `9e91054327e3c66a72399d1d0a5a19f544df70a9` — preserve the original repair failures.
3. `2700c2ca78d4587fecaa0a35652ec736d1a6b014` — record corrected-contract owner acceptance.
4. `dd287135e3142207dc6655cbd36a81471b48f68d` — seed-aware reader and named reread.
5. `ceee1446f18ae9b7134005089046a5a4d69e10ae` — aggregate bounds and complete reread regressions.

The final commit changes only the reader and
`tests/data_sources/test_ea001_operational_evidence_integrity_repair.py`.
No amend, reset, rebase, cherry-pick, merge, push, or other history rewrite was
performed.

## 3. Preserved preliminary evidence and dated correction

The preliminary report correctly recorded the original 12 red failures on the
pre-repair reader and the subsequent 36 focused passes at `dd28713`. Those
failures cover the same-length seed-attempt mutation, every seed dependency,
candidate replacement, source/temporal seed disagreement, omitted required
seed, and the previously absent named-reread method. That evidence remains
valid and is preserved here.

Follow-up on 2026-09-05: the preliminary report was not a completion result. It
had not run the full repository or dual-clean-checkout gates, had not produced
a separate corrected seed-aware digest, and overstated named-reread coverage.
Independent review also found that horizon and seed closures were checked
separately, while their merged union could exceed the fixed aggregate limits.
Sections 4–12 replace those premature claims with observed evidence.

## 4. Aggregate-budget red-before evidence

The public-path regression used one pre-horizon observed seed followed by one
in-horizon empty snapshot. Production constants were not changed; process-local
patches made the boundary economical. Ordinary combined material contained
exactly 10 artifacts and 15,490 metadata bytes and reread unchanged.

Before the runtime fix, at exact starting HEAD `dd28713`, this command was run:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/data_sources/test_ea001_operational_evidence_integrity_repair.py \
  -k 'aggregate_budget or named_reread' -q
```

Observed: five reported failures, six passes, and twelve deselections. Four
failures were the genuine aggregate defect: artifact and metadata one-less
limits each failed to refuse through both `read_material` and
`inventory_token`. The fifth was a test-construction `StopIteration` in the
substitution case; it was corrected before the production repair and is not
reported as a product defect. Exact-limit 10-artifact and 15,490-byte valid
twins passed before and after the repair.

## 5. Repaired aggregate mechanism and fixed-after result

`_merge_materials` now accounts one aggregate descriptor set while combining
horizon and seed closure. Before retaining a new merged descriptor it:

- rejects a conflicting descriptor for the same `(kind, logical_id)`;
- counts an equal shared descriptor once;
- refuses the next unique descriptor above 16,384; and
- refuses the next non-payload metadata descriptor above 64 MiB.

The seed remains outside the 4,096 in-horizon-attempt count. No dependency is
dropped to meet a bound. The public capture refusal remains the existing
`OPERATIONAL_EVIDENCE_LIMIT_EXCEEDED` error. Exact limits are inclusive.

After the runtime change, the complete repair file produced `23 passed in
2.28s`. Both public paths refuse at 9 artifacts or 15,489 metadata bytes,
while the 10-artifact and 15,490-byte twins remain valid; every admitted
material twin completes an unchanged named reread.

## 6. Permanent named-material reread matrix

Permanent tests now establish:

| Requirement | Observed result |
| --- | --- |
| Ordinary equality | returned exactly equal material |
| Same-read metadata digest/parse | every named path read exactly once |
| Changed metadata | `OPERATIONAL_EVIDENCE_NAMED_MATERIAL_MISMATCH` |
| Substituted metadata | `OPERATIONAL_EVIDENCE_NAMED_MATERIAL_MISMATCH` |
| Missing named artifact | `OPERATIONAL_EVIDENCE_NAMED_MATERIAL_UNAVAILABLE` |
| Symlink/unsafe named artifact | `OPERATIONAL_EVIDENCE_NAMED_MATERIAL_UNAVAILABLE` |
| Forged nested strict integer | refused before the first filesystem read |
| Unrelated later additions | frozen named material still matched |
| Current membership over patched capture bound | frozen named material still matched; inventory capture refused |
| Shared payload/origin run | one envelope retained with both required runs |
| Write effects | byte/mtime inventory identical before and after |
| Network effects | success with socket construction forbidden |
| Sensitive-path disclosure | temporary source path absent from typed errors |

The method rereads only descriptor-named artifacts, accepts no path, performs
no membership selection, and makes no current/latest claim.

## 7. Seed fencing, parity, and deterministic behavior

The earlier permanent matrix remains green for attempt, attempt-run,
raw-origin-run, envelope, payload, extraction, and observation-content
mutation: each changes the seed-aware token or refuses typed. Initial and final
token invocations rediscover the source seed independently. Exact temporal ID
agreement succeeds; substitution or omission of a required ID yields
`OPERATIONAL_EVIDENCE_SEED_PARITY_MISMATCH`.

Repeated raw bytes remain distinct acquisition candidates. The origin run is
retained when reused content requires it. An in-horizon selected occurrence
adds no pre-horizon seed; no eligible observation produces no seed. Existing
tests preserve the 4,096 in-horizon behavior and permit longer out-of-horizon
history. Reversed filesystem enumeration and Python hash seeds `1`, `7`, and
`12345` produced identical seed-aware serialization.

## 8. Independent lower-material reproductions

The original accepted in-horizon source/temporal reproduction was run in a
fresh disposable store:

| Reproduction | Bytes | SHA-256 | Shape |
| --- | ---: | --- | --- |
| Original lower material | 24,766 | `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7` | source `10/2/2`; temporal `2/2` occurrences/attempts |
| Corrected seed token plus source material | 11,528 | `494801a6aaed53f49768f9fe143fc7bb80f327fb6a332da3b1a2b0354a12272f` | token 5 members; material 5 artifacts, 1 attempt, 1 run, 1 observation |

The corrected value was reproduced in independent disposable stores for hash
seeds `1`, `7`, and `12345`, reversed enumeration, fresh base-only checkout,
and fresh all-extras checkout. Every run returned the same 11,528 bytes and
digest. The original value also reproduced identically in both clean
checkouts. The old digest is retained as historical in-horizon material proof;
it is not used as proof of the corrected seed fence.

## 9. Focused and module verification

All commands targeted tested implementation `ceee1446` using Python 3.13.11:

| Gate | Exact result |
| --- | --- |
| Full repair regression file | 23 passed |
| Reader, repair, cross-seam reproduction, architecture, temporal selection | 69 passed in 7.74s |
| Complete temporal plus EA architecture | 100 passed in 37.38s |
| Complete data sources, restricted | 384 passed; 1 localhost-bind setup error in 275.86s |
| Permitted isolated data-source loopback | 1 passed in 1.97s |

The focused 69-test command was:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/data_sources/test_ea001_operational_evidence_integrity_repair.py \
  tests/data_sources/test_ea001_operational_evidence_reader.py \
  tests/test_ea001_slice_a_reproduction.py \
  tests/test_ea001_slice_a_architecture.py \
  tests/temporal_state/test_ea001_selection_material.py -q
```

The complete data-source command was the same pytest configuration against
`tests/data_sources`. The isolated loopback command named exactly
`TestRealLoopbackTransport::test_get_redirect_refusal_and_proxy_isolation`
and ran with permitted localhost binding. The restricted aggregate remains an
aggregate with one environmental setup error; it is not relabelled as an
uninterrupted passing suite.

## 10. Working-checkout full verification

At exact HEAD `ceee1446f18ae9b7134005089046a5a4d69e10ae`:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider tests/ -ra
```

Collected 3,550 tests. Observed `3549 passed, 1 error in 1328.09s`. The sole
error was sandbox denial while binding `127.0.0.1` for the known loopback
fixture. Its exact separately permitted rerun passed (`1 passed in 1.97s`).
There were no functional test failures or skips. This accounting deliberately
does not describe the restricted aggregate itself as uninterrupted green.

`pip check` reported no broken requirements. `compileall -q backend` compiled
all 113 backend Python files. Working-tree and complete
`b3e27cb..ceee1446` whitespace checks passed.

## 11. Fresh base-only checkout

A fresh local clone was detached at exact `ceee1446`. A new virtual environment
installed only `requirements.txt` and `requirements-dev.txt`. The complete
suite command was identical to Section 10.

Observed: `3514 passed, 35 skipped, 1 error in 816.13s`. All 35 skips were the
declared CAD/PDF optional-dependency paths: four PDF-runner, four STEP-runner,
one PDF-availability, eighteen PDF-extractor, six STEP-extractor, and two
structural STEP claims. The only error was the known restricted loopback setup;
its exact separately permitted rerun passed (`1 passed in 0.72s`).

`pip check`, backend compilation, both whitespace checks, original and
seed-aware reproductions, exact detached HEAD, and clean Git status all passed.
The temporary checkout was used only for verification and deleted afterward.

## 12. Fresh all-extras checkout and CAD/PDF coverage

A separate fresh local clone was detached at exact `ceee1446`. Its fresh
environment installed base/development requirements, then separately installed
the accepted hash-pinned `requirements-cad.txt` and `requirements-pdf.txt` with
`--require-hashes`.

Observed complete suite: `3549 passed, 1 error in 819.23s`; there were no skips
or functional failures. The sole error was the known restricted loopback setup;
its exact separately permitted rerun passed (`1 passed in 0.76s`).

Explicit optional coverage used:

```text
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider -m 'cad or pdf' \
  tests/data_sources tests/structural_evidence -q
```

Result: `35 passed, 577 deselected in 39.38s`. This exercised real CAD/STEP and
PDF paths. `pip check`, backend compilation, both whitespace checks, both
reproductions, exact detached HEAD, and clean Git status passed.
The temporary all-extras checkout was deleted after verification.

## 13. Preservation, residual limitations, and owner gate

Independent read-only verification loaded and checked the authoritative model
before and after byte snapshots. Observed:

- exactly 36 model records;
- revision `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
- FRG/FLD/FLW exactly `1/1/0`;
- whole-ledger aggregate `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`;
- FL disclosure exactly 660,516 bytes and SHA-256
  `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`;
- byte inventory identical before and after verification; and
- no milestone-range change to models, source fixtures/evidence, temporal
  data, bindings, interpretations, memberships, or protected artifacts.

The ignored `.claude/settings.local.json` remained untouched; its observed
SHA-256 is `abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.
The exact public source-reader exports remain the two accepted names. The
remaining test limitation is disclosed, not hidden: three restricted complete
suite columns each contain the one localhost setup error, with the same exact
test separately passing under permission. No environmental condition prevented
the requested functional test from executing.

This report is intentionally uncommitted. Owner acceptance of this repair is
the only next decision. Slice B requires separate authorization after repair
acceptance; Slice C remains unauthorized.

END OF EA-001 SLICE A INTEGRITY REPAIR COMPLETION REPORT
