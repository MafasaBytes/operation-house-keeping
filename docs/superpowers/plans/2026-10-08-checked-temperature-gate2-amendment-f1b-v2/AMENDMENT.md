# Checked temperature Gate 2: F1b amendment v2 (dispositions A and B)

Date: 2026-10-08. Amendment id: `gate2-f1b-2026-10-08`, package revision v2.
Status: successor amendment implementing owner-approved dispositions A and B;
package contents not separately owner-reviewed. This package edits no frozen file
and does not edit the v1 package, which stays as retained history. It records two
expectation/fixture changes and one bounded L1 continuation. The machine-readable
form is [inventory.json](inventory.json), bound by [MANIFEST.json](MANIFEST.json).

## 0. Supersedes v1

Predecessor package [v1](../2026-10-08-checked-temperature-gate2-amendment-f1b/AMENDMENT.md):
`AMENDMENT.md` `8a6290560d9688170d2e6e48545f7bb7c4afaa3f5cd7a8f0becb228f592a34b6`,
`inventory.json` `3e21bd4436db632576d6cc175f07044e98a43a74bbaf0190d9a353fc5cd0c3de`,
`MANIFEST.json` `cf7a378d4d90c5d1ef84183692fb00e9c3ba5adac722a5a469ef6a3bf9eb7663`.
No expectation, pin, digest, argv or schedule entry changes. Disclosed corrections:

1. Status wording (v1 line 3 and MANIFEST status "owner-approved successor
   amendment") replaced as above.
2. Document retention: v1 "Numerical document ceilings are unchanged" is withdrawn; §8.
3. "Exactly one schema violation" and "first invalid record" are relabelled as
   static standalone predictions, not executed results; independent emulation added; §5.
4. F1b.2 coverage limit added (AMENDMENT and `new_invocations[0].coverage_limit`); §5.
5. Twin legality: FX1.1 control and the two coordinated differences stated; §5.
6. Contract citations corrected (v1 cited §12.6 alone for input legality and called
   `target` a free string); closure rule restated as executed; §4, §5.
7. Evidence pins added: `reports/supervisor.json`, `streams/F1b.1.stdout`,
   `reports/retention-measurement.json` (plus the FX1.1 control result); "38 objects" note; §1.
8. New §6a "Continuation harness assumptions" and inventory key `continuation_harness`.
9. Storage reconciliation and headroom; §7.
10. Owner authorization: v1 presented relayed paraphrase as verbatim; v2 quotes only
    the owner's exact sentences; §2.

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
| v1 package MANIFEST | [v1 MANIFEST](../2026-10-08-checked-temperature-gate2-amendment-f1b/MANIFEST.json) | `cf7a378d4d90c5d1ef84183692fb00e9c3ba5adac722a5a469ef6a3bf9eb7663` |

Checkpoint HEAD `4d6ab13c46642e9771199dced7d312ac94bbbb2f`; current real build
(`metadata/candidate-build.json`) `fa14f8eca32c75ba8a0928d3261de20a989c8f3fa1c7eceaf50c8541a30b62f2`;
accepted implementation `8414f4d5f70a774b5c9cef1da82ce4ff55fc1cf8`. Workspace
`WS=/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate2-4d6ab13`.
Every workspace evidence file is pinned by full SHA-256 in `inventory.json` key
`evidence`. v2 adds `reports/supervisor.json` (`9ef5ed6e...`, source of the
581.158 s figure), `streams/F1b.1.stdout` (0 bytes, `e3b0c442...`),
`reports/retention-measurement.json` (`3ae69509...`) and `reports/result-FX1.1.json`
(`3e52a540...`). The attribution proposal's "38 objects" means 37 objects plus
`request.json` (38 files); this amendment states 37 objects.

## 2. Owner authorization

Owner message, 2026-10-08, quoted:

> One semantic/fixture L1 continuation is authorized. It counts as a top-level
> launch but does not consume an infrastructure-retry slot. The original failed
> attempt remains consumed; no refund or reset.

The approval of dispositions A and B, the limitation to the two named
expectation/fixture changes, and the statement that Gate 2 acceptance remains a
separate owner decision are the relayed record of the owner decision, not
verbatim quotation (v1 presented them inside quotation marks).

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
  target `/binding`; every other field matched; stdout 0 bytes.
- Attribution of `/binding` to claim
  `912499985aef84a9c158a48037f75e0018445211c8c591a183a28836e81ce58e` (a derived
  `state_hold` claim, `b_suspect` maxItems 2) is inferred from source: diagnostics
  carry no object digest.
- [v4 witnesses](../../specs/2026-10-04-checked-temperature-contract-preparation-v4/witnesses.json)
  case F1b expects only "refuse SCHEMA_INVALID" (status original, predecessor F1,
  witness W16). [CONTRACT v4](../../specs/2026-10-04-checked-temperature-contract-preparation-v4/CONTRACT.md)
  §12.2 lists `target` as a diagnostic field; its type comes from
  [v4 schemas.json](../../specs/2026-10-04-checked-temperature-contract-preparation-v4/schemas.json)
  `ct.diagnostic.v1` `target` `{"type":"string","maxLength":256}`. No value is
  prescribed. The historical test
  `tests/checked_temperature/test_selection_witnesses.py::test_f1b_three_hypotheses_schema_invalid`
  asserts only the code.
- The `/hypotheses` detail was introduced by the Gate 2 plan manifest, not the
  contract. No implementation discrepancy is claimed. The failed comparison
  (`reports/result-F1b.1.json`, `streams/F1b.1.stdout`, `streams/F1b.1.stderr`)
  stays retained and charged.

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
- Closure, as `metadata/construct-F1b.2.py` executed it: from the request and
  authority roots every typed `{kind, sha256}` reference is followed; `nm.evidence.v1`
  and non-JSON content are non-edge leaves; no x-edge exception was applied (none
  is needed, because stage 2 fires first). Result: 28 reachable, none missing or
  unreferenced.
- Static standalone prediction (third-party jsonschema 4.26.0 under the system
  `python3`, not the approved interpreter; and a reimplemented traversal), not
  executed by the application: exactly one schema violation (model `16bb5ea1...`
  `/hypotheses` maxItems), and the model is the first invalid record under
  `checked_runtime.resolve` FIFO order (14 records loaded before it). The launch
  tests code/stage/target only; attribution of `/hypotheses` to the model is
  inferred from source, since diagnostics carry no object digest.
- Independent mathematical emulation
  `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/experiments/mathematics/2026-10-08-gate2-f1b-continuation/precedence_emulator.py`
  (`f4e9aa0256ab4db942740c4f4d19ac2f5d9fc56843774372524d3356c47a0673`; outputs
  `out-F1b.json` `a56a1f4bb8155b4133d423410a2d22be6243ca210366284e39ef19fd5626a6f7`
  and `out-F1b.2.json` `7fa14a900feab7cb4a6e317e09cdd619a0fa532aba6746cb84c234b466e85923`
  in the same directory) reproduced the same first refusal for both packets
  (F1b `/binding`, F1b.2 `/hypotheses`), including the stage-1 and stage-3 checks.
  It is also static, not an application execution.
- Input legality of the unsupplied required `state_hold` cores: CONTRACT v4 §4.2
  derives the required claim cores from the request (CB1: a missing declaration
  gives `declaration_missing`), and exit class 0 means "completed (including
  withheld or blocked)" (CONTRACT.md line 420). §12.6 is the self-containment
  clause for such a withheld or blocked selection.
- Coverage limit: isolates the bound as the FIRST refusal only; any 3-hypothesis
  model also repeats an account_kind, which stage 4 would refuse
  (ACCOUNT_KIND_CONSTRAINT_VIOLATED, [checked_runtime.py](../../../../applications/bounded_decision_workflow/checked_runtime.py):296-297),
  so no input can make maxItems the only violated rule.
- Twin legality: the untouched passing control is FX1.1 (passed in launch 1,
  `reports/result-FX1.1.json`). F1b.2 differs from FX1 by two coordinated
  differences: a third hypothesis duplicating H2 is added; the two `state_hold`
  claims and their eight dependents are removed. This follows the coupled-constraint
  rule of the [adversarial-twin skill](../../../../.claude/skills/adversarial-twin-construction/SKILL.md)
  (checklist item 2). Byte-level digests of the remaining claims and their
  dependents also differ from FX1 because claim cores bind the exact model
  revision (§4.2).
- This steward re-verified every packet file hash and size against
  `metadata/binding-F1b.2-selection.json` (v1) and the WS evidence pins (v2).
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

## 6a. Continuation harness assumptions

Scripts under `{WS}/metadata` (SHA-256 in `inventory.json` key `continuation_harness`):
`make-continuation-driver.py` `6c97f609...`, `continuation-supervisor.py` `d298c3bc...`,
`continuation-L2-child.py` `b0d81fea...`, `continuation-L2-supervisor.py` `283c7bc5...`,
`continuation-closeout.py` `26f95499...` (as observed by the steward at freeze; four of
these changed at 12:30 +0200 after the caller's hash list, see below); and
`continuation-driver.py` `f3765f30...`,
`continuation-driver.diff` `1372435a...`, `continuation-pins.json` `0b9f153a...`,
`continuation-driver.sha256` `cbc18a0d...`. The last four are a v1-bound generation
(they pin the v1 inventory); superseded by the regeneration recorded in the
pre-launch record.

Pin discrepancy, disclosed: the hash list supplied to the steward gave
`make-continuation-driver.py` `cb17bc36...`, `continuation-supervisor.py` `565ad867...`
and `continuation-closeout.py` `3a939a48...`; `continuation-L2-supervisor.py` hashed
`ad683ba5...` when first read. All four were rewritten in the workspace at
2026-10-08 12:30 +0200 (not by the steward) and no longer match. v2 pins the bytes
observed at freeze and keeps the superseded values in `continuation_harness`.

- (a) Launch-1 in-memory state is reconstructed by re-running the frozen recipes
  for FX1, F1b and UN1 and requiring byte equality of request, objects and pins with
  the retained packets, plus manifest-integrity and build checks on the retained
  FX1/UN1 bundles. Verified by the launch; it stops on inequality before any CLI attempt.
- (b) The later synthetic evidence chains are rebuilt under the fresh base
  `construction/later-continuation`, because the chain builder refuses existing
  directories: four chains (60, 57.6, 1000, 1000.000001; about 157.7 KB, 40 files,
  22 directories each). UN1 reconstruction equality verifies that the 60 chain's
  evidence bytes equal launch 1's; the other three are used only by remaining cases
  and are not compared with launch-1 chains.
- (c) The coexistence accounting list names the frozen driver, admin-setup,
  supervisor and closeout scripts in `/tmp` plus the three preflight probes (seven
  files); the continuation scripts are inside the workspace.
- (d) The continuation clock starts at 581.158 s (supervisor figure); the driver's
  own 580.797 s (`reports/L1-summary.json`) is smaller, so this is conservative.
- (e) The driver runs manifest order with the on-demand SUP1.1 trigger and does
  not separately assert equality with `continuation_order`. The closeout compares
  the executed order with it after the fact. Static reading: the superseded closeout
  `3a939a48...` had no such comparison; the closeout pinned here (`26f95499...`)
  checks the executed ids as a prefix of `continuation_order` read from the
  continuation pins file, and records `null` if the pins file lacks that list, so
  it depends on the regenerated pins carrying it.
- (f) The CLI ceiling assertion is 235, an interpretation: 233 base plus the two
  owner-authorized attempts. Any further attempt stops the run. The continuation
  consumes one of the two relaunch allowances (base 2, maximum 4), leaving one.
  The eight retry slots remain unused, but only six further child attempts would
  fit under the unchanged 241/245 maxima.

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

Storage. v1 stated 28,145,980 logical bytes, 3,823 files, 386 directories
"before the continuation" and recorded no measurement time. That figure reconciles
exactly with the measurement at 2026-10-08 12:15:22 +0200
(`experiments/.../measure-ws-output.json`: 28,315,288 B, 3,859 files) less the
F1b.2 packet (104,889 B, 28 files) and eight construction/harness files present at
that time and omitted by v1 (64,419 B): `construct-F1b.2.py` 14,576,
`F1b.2-construction.json` 3,475, `binding-F1b.2-selection.json` 7,283,
`continuation-L2-child.py` 791, `continuation-L2-supervisor.py` 6,982,
`continuation-closeout.py` 10,683, and two files then of 16,154 and 4,475 B
(inferred from sizes and file times to be earlier versions of
`make-continuation-driver.py` and `continuation-supervisor.py`, since rewritten).
Ceilings: 805,306,368 logical / 48,000 files / 1,500 directories, 1 GiB allocated.

F1b.2 is an 89th selection packet, absorbed by the plan's headroom: with 89
selection packets and 235 + 4 stream slots the amended component sum is
749,273,088 B and headroom 56,033,280 B (frozen 747,503,616 / 57,802,752); the
input-file estimate is 40,115 of 48,000. Projected directories 878 of 1,500. The
pre-launch record will re-measure immediately before launch. Gate 1 (19 of 40)
stays separate. Memory group `/sys/fs/cgroup/memory/ct-gate2-4d6ab13` unchanged:
1,073,741,824 memory and memory+swap, hierarchy 1, failcnt 0, peak 316,899,328.

## 8. Unchanged, and document retention

Every other matrix, support and control row; all runtime ceilings and stop rules;
the environment (CPython 3.13.11, executable `47f615b1be25c94e9304ccd9339f9a8ef21d2194fca32643c441fb2dad290264`,
lock `7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817`);
checkpoint; workspace; and the F3b/DG1 coverage limits.

Document retention. The frozen plan (consolidated plan line 179) caps the
repository document-retention scope at three files, zero new directories and
1,048,576 logical bytes. This owner-instructed freeze EXCEEDS the frozen file and
directory counts: v1 added 1 directory and 3 files; v2 adds a second directory
and 3 more files (total 2 directories, 6 files). The exact byte total is recorded
in `MANIFEST.json` key `document_retention` (it includes MANIFEST.json itself);
bytes stay within the 1,048,576 byte cap. The count caps are exceeded by owner
instruction; the owner may confirm or narrow this at the gate. `MANIFEST.json`
is the project's standard package binding file (frozen-artifact-verification
practice), not a file the owner named.

## 9. What this amendment does not do

- No oracle, contract, schema, policy, witness or application change.
- No use of an infrastructure-retry slot, and no refund or reset of the failed F1b.1 attempt.
- No Gate 1 borrowing or transfer.
- No acceptance: Gate 2 acceptance remains a separate owner decision.
- No execution, staging or commit; no edit of frozen, v1 or retained material.

END OF GATE 2 F1B AMENDMENT V2
