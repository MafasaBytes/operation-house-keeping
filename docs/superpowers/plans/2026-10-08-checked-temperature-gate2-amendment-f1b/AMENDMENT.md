# Checked temperature Gate 2: F1b amendment (dispositions A and B)

Date: 2026-10-08. Amendment id: `gate2-f1b-2026-10-08`. Status: owner-approved
successor amendment. This package does not edit any frozen file. It records two
expectation/fixture changes and one bounded L1 continuation. The machine-readable
form is [inventory.json](inventory.json), bound by [MANIFEST.json](MANIFEST.json).

## 1. Predecessors and governing pins

| Role | Path | SHA-256 |
|---|---|---|
| Frozen plan | [2026-10-08 plan](../2026-10-08-checked-temperature-gate2-consolidated-plan.md) | `a5e2af15e70638b06538190490e677d3da4b0308d3d783032a82ab475672c2ac` |
| Frozen manifest (425,621 B) | [2026-10-08 manifest](../2026-10-08-checked-temperature-gate2-manifest.json) | `9b22e108b0a7cd1b38b5d9d380581c32a9491418a1bd3c756e252cefe71a17b0` |
| Earlier plan | [2026-10-05 plan](../2026-10-05-checked-temperature-gate2-consolidated-plan.md) | `61c4c0e806b1472da367b1cc309fa0ff6558845c3d4077f98219beec840d59b5` |
| Earlier manifest | [2026-10-05 manifest](../2026-10-05-checked-temperature-gate2-manifest.json) | `7f6a236f0f07cdc6c51e89830632bad8e045cdf7d52aec0c88834158a82a9d09` |
| v4 package | [v4 MANIFEST](../../specs/2026-10-04-checked-temperature-contract-preparation-v4/MANIFEST.json) | `9e0afa328c3281fd468be21911f7840a74a35cdafd616b3f79605eaebd5df529` |
| Amendment C1 | [C1 MANIFEST](../../specs/2026-10-05-checked-temperature-contract-amendment-c1/MANIFEST.json) | `791b4035807ce032f7852447df0e0b7d9324c8cb90d52bc8a1b6ebac42ab9d1a` |
| Amendment C2 | [C2 MANIFEST](../../specs/2026-10-05-checked-temperature-contract-amendment-c2/MANIFEST.json) | `6252a2da6058b443db070954e7bf2a2ae075aba652ce6b09cabc0eb1b323bec6` |

Checkpoint HEAD `4d6ab13c46642e9771199dced7d312ac94bbbb2f`; current real build
(`metadata/candidate-build.json`) `fa14f8eca32c75ba8a0928d3261de20a989c8f3fa1c7eceaf50c8541a30b62f2`;
accepted implementation `8414f4d5f70a774b5c9cef1da82ce4ff55fc1cf8`. Workspace
`WS=/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate2-4d6ab13`.
Every workspace evidence file is pinned by full SHA-256 in `inventory.json` key
`evidence`, including `reports/F1b-attribution-proposal.md` (9,995 bytes)
`2f1ea0a0f85bfbcf983a45057fb6e7dba34be4f7893e6114c2e24e3f25d6ede6`.

## 2. Owner authorization (recorded verbatim)

"Owner approves dispositions A and B and one bounded L1 continuation under the
existing Gate 2 resource ceilings." "This approval covers only the two named
expectation/fixture changes. No other oracle, contract or application changes
are authorized." The continuation "counts as a top-level launch but does not
consume an infrastructure-retry slot. The original failed attempt remains
consumed; no refund or reset." Gate 2 acceptance remains a separate owner decision.

## 3. Old to new map

| Item | Old (frozen manifest) | New (this amendment) | Status |
|---|---|---|---|
| `invocations[128]` F1b.1 expected `diagnostic_template.target` | `/hypotheses` | `/binding` | amended (A) |
| F1b.1 coverage label | none | coupled derived-claim refusal coverage | amended (A) |
| F1b.1 re-execution | failed attempt 1 (retained) | attempt label `F1b.1.a2` | continuation |
| F1b.2 invocation | absent | isolated model hypothesis-count bound (maxItems 2) | new (B) |
| F1b.2 case inventory entry | absent | mirrors case F1b (W16) | new (B) |
| Contract, schema, policy | v4 + C1 + C2 | unchanged | unchanged |
| Witness `witnesses.json` F1b | "refuse SCHEMA_INVALID" | unchanged; both rows satisfy it | unchanged |

Original F1b.1 expectation, preserved verbatim (manifest row 128, key `expected`):

```json
{"bundle":"absent for evaluate/replay refusal; untouched source for verify refusal","diagnostic_template":{"code":"SCHEMA_INVALID","exit_class":3,"stage":2,"target":"/hypotheses"},"exit":3,"source_semantics":"refuse SCHEMA_INVALID","stderr":"one canonical ct.diagnostic.v1 plus LF","stdout":"empty"}
```

The amended F1b.1 expectation differs only in `"target":"/binding"`. The full
original row is copied verbatim as `amended_invocations[0].original`.

## 4. Basis for disposition A

- F1b.1 runs `checked-selection-evaluate` on packet F1b (request pin
  `451c059c35b4cf609d671572a72476775ebe4395b1867ead885e26cb4ca2af2b`, authority
  pin `c5fbdb8af9b55ab21d1b686afd2690c41280ccb0cc03ec68dc24130cf1f85160`, 37 objects).
- Observed at L1 launch 1 (2026-10-08): exit 3, `SCHEMA_INVALID`, stage 2,
  target `/binding`; every other field matched. The packet is a 3-hypothesis model
  with its derived `state_hold` claims; under FIFO resolution the first stage-2
  refusal is the coupled claim binding (`b_suspect` maxItems 2).
- [v4 witnesses](../../specs/2026-10-04-checked-temperature-contract-preparation-v4/witnesses.json)
  case F1b expects only "refuse SCHEMA_INVALID" (status original, predecessor F1,
  witness W16). [CONTRACT v4](../../specs/2026-10-04-checked-temperature-contract-preparation-v4/CONTRACT.md)
  §12.2 defines `target` as a free string. The historical test
  `tests/checked_temperature/test_selection_witnesses.py::test_f1b_three_hypotheses_schema_invalid`
  asserts only the code.
- The `/hypotheses` detail was introduced by the Gate 2 plan manifest, not the
  contract. No implementation discrepancy is claimed. The failed comparison
  (`reports/result-F1b.1.json`, `streams/F1b.1.stderr`) stays retained and charged.

## 5. Disposition B: F1b.2 construction and checks

- Packet `{WS}/inputs/F1b.2/selection`: `request.json` plus 27 objects, 28 files,
  104,889 bytes. Request pin `c0ea4152c7ef2d1a25749b405ed45337bafe22f05217f203c671fe8a969fff56`
  (2,303 B); authority pin `6e0c5ce6aa9460f00f1b6be2cbc7929ceb7bc684e43faaceb79cb5b9cae5f554`
  (577 B); same build `fa14f8ec...`; construction order request then evaluation_authority.
- Built from the retained F1b packet by removing the two `state_hold` claims
  (`912499985aef...`, `caaa3e08e9c7...`) and their eight dependents: declarations
  `7d31bdb2...`, `de579f5f...`; evidence items `cf79e664...`, `e20c8bc0...`;
  contents `8e887c24...`, `f124e640...`; reviews `4f78ab79...`, `cf37ddae...`.
  Full digests are in `inventory.json`.
- Checks recorded by `reports/F1b.2-construction.json`: closure closed (28
  reachable, none missing or unreferenced under the typed-reference rule); exactly
  one schema violation (model `16bb5ea1...` `/hypotheses` maxItems); that model is
  the first invalid record under `checked_runtime.resolve` FIFO order (14 records
  loaded before it). Unsupplied required `state_hold` cores are legitimate under
  CONTRACT v4 §12.6. This steward re-verified every packet file hash and size
  against `metadata/binding-F1b.2-selection.json`.
- Expected: exit 3; `{"code":"SCHEMA_INVALID","exit_class":3,"stage":2,"target":"/hypotheses"}`;
  stdout empty; one canonical `ct.diagnostic.v1` plus LF on stderr; no output directory.
- Case entry mirrors manifest case F1b: obligation "boundary-sized inputs and
  plus-one refusals", witness W16, source `witnesses.json` F1b, source_expected
  "refuse SCHEMA_INVALID"; status new. The invocation row carries one extra key,
  `packet: "F1b.2"`, which frozen rows do not have; the driver uses it to locate the packet.

## 6. Attempt labels and unexecuted schedule

The continuation re-executes F1b.1 as `F1b.1.a2` (same argv, pins and packet as
the retained `metadata/command-F1b.1.json`). Original `result-F1b.1.json`,
`command-F1b.1.json` and `streams/F1b.1.*` stay untouched. F1b.2 uses id `F1b.2`.

The 128 passing commands (`invocations[0..127]`) are not repeated. The ordered
schedule has 112 entries: `F1b.1.a2`, `F1b.2`, then 104 CLI ids (86 matrix with
`SUP1.1` inserted immediately before `RE4.1`, then 17 controls), then 4 internal
calls (IC1, PF1, PF2, PF3), then 2 static decoder checks (F3b-regions, F3b-cut).
The list was generated from the frozen manifest and `stopped-closeout.json`.
The remaining schedule resumes only if both F1b.1.a2 and F1b.2 match completely.
Any unexpected result stops the affected sequence for owner review. L2 (one pytest
launch over the five `legacy_scope` paths, reservation unchanged) runs only if L1 completes.

## 7. Cumulative accounting

| Quantity | Before | Authorized delta | Projected | Ceiling |
|---|---|---|---|---|
| Top-level launches | 1 | +1 continuation (+1 L2 if reached) | 3 | 4 (base 2) |
| CLI attempts | 129 (128 pass, 1 fail consumed) | +106 (1 + 1 + 104) | 235 = 233 base + 2 owner-authorized | 241 |
| Internal calls | 0 | +4 | 4 | 12 if all retries internal |
| Combined CLI + internal | 129 | +110 | 239 | 245 |
| Infrastructure retry slots | 0 of 8 | 0 | 0 of 8 | 8 shared |
| Pytest launches | 0 | +1 if L2 reached | 1 | 2 |
| Git/identity helpers | upper bound 907 | cumulative | continues | 10,000 |
| L1 wall seconds | 581.158 | clock continues, no reset | from 581.158 | 14,400 |

Storage measured 2026-10-08 before the continuation: 28,145,980 logical bytes,
3,823 files, 386 directories (plus accounted external coexistence files), against
805,306,368 / 48,000 / 1,500 and 1 GiB allocated. The frozen F1b.2 packet adds
104,889 bytes, 28 files, 3 directories. Gate 1 (19 of 40) stays separate. Memory
group `/sys/fs/cgroup/memory/ct-gate2-4d6ab13` unchanged: 1,073,741,824 memory and
memory+swap, hierarchy 1, failcnt 0, peak 316,899,328.

Arithmetic consequence: at 239 projected combined attempts, at most six further
child attempts fit under the unchanged 245 combined and 241 CLI maxima, although
zero of eight retry slots are used.

## 8. Unchanged

Every other matrix, support and control row; all ceilings and stop rules; the
environment (CPython 3.13.11, executable `47f615b1be25c94e9304ccd9339f9a8ef21d2194fca32643c441fb2dad290264`,
lock `7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817`);
checkpoint; workspace; and the F3b/DG1 coverage limits.

Retention scope: the frozen plan's three-file document-retention scope is extended
by this owner-instructed package, which adds one new directory and three new files
(`AMENDMENT.md`, `inventory.json`, `MANIFEST.json`). Numerical document ceilings
are unchanged.

## 9. What this amendment does not do

- No oracle, contract, schema, policy, witness or application change.
- No use of an infrastructure-retry slot, and no refund or reset of the failed F1b.1 attempt.
- No Gate 1 borrowing or transfer.
- No acceptance: Gate 2 acceptance remains a separate owner decision.
- No execution, staging or commit; no edit of frozen or retained material.

END OF GATE 2 F1B AMENDMENT
