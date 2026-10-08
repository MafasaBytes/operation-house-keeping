# Checked temperature Gate 2: F1b dispositions executed, L1 continuation stopped at F5a.1

2026-10-08. Handoff for owner review. Execution record only; not acceptance. Checkpoint `4d6ab13c46642e9771199dced7d312ac94bbbb2f`; real build `fa14f8eca32c75ba8a0928d3261de20a989c8f3fa1c7eceaf50c8541a30b62f2` (unchanged from launch 1; accepted implementation `8414f4d5f70a774b5c9cef1da82ce4ff55fc1cf8`; historical launch 19 `d81acac6f40f97670c23d08df15b3d1f568df5433bdb8ac3b55961f33d27f23c`). Workspace `WS` = `~/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate2-4d6ab13`.

## 1. Verified before execution

| Record | SHA-256 | Status |
|---|---|---|
| Frozen plan `docs/superpowers/plans/2026-10-08-checked-temperature-gate2-consolidated-plan.md` | `a5e2af15e70638b06538190490e677d3da4b0308d3d783032a82ab475672c2ac` | unchanged |
| Frozen manifest `…-gate2-manifest.json` (425,621 B) | `9b22e108b0a7cd1b38b5d9d380581c32a9491418a1bd3c756e252cefe71a17b0` | unchanged |
| Stopped closeout `WS/reports/stopped-closeout.md` / `.json` | `32bf3c3982c19b4ba900c7b1d1953b4dedb26380100f9e71bedf2bb31b45b80c` / `2ed8b8b4c0a22b2f19a38473690fd82adf5391bad7a1d14b57e242fb47852a29` | unchanged |
| F1b attribution proposal `WS/reports/F1b-attribution-proposal.md` (9,995 B), full hash | `2f1ea0a0f85bfbcf983a45057fb6e7dba34be4f7893e6114c2e24e3f25d6ede6` | unchanged |
| Original F1b.1 failure `WS/reports/result-F1b.1.json`; `streams/F1b.1.stderr` | `f5f1c35b3dc5510a5be8b06952ee8b95d93abd8ac36f10cf53ca6b7fef93393b`; `51c1304070ffecdfd3374f69a80228864abf4db26df42b90ef86c12326486103` | retained, charged |
| Manifest `sources`, `preservation.unrelated_files` (incl. `.git/index` `e2256ef4…`), `predecessors` | 60 entries | 0 drift, before and after |

The pre-continuation evidence audit reconciled "128 passing checks" with command identities: 128 distinct invocation IDs, each one process attempt, with result, command and stream files; the 104 remaining IDs equal manifest order minus the executed set. Gate 1 (19 of 40) untouched.

## 2. Frozen amendment and F1b.2 construction

- Successor packages (untracked, repository): `docs/superpowers/plans/2026-10-08-checked-temperature-gate2-amendment-f1b/` (v1: AMENDMENT.md `8a6290560d9688170d2e6e48545f7bb7c4afaa3f5cd7a8f0becb228f592a34b6`, inventory.json `3e21bd4436db632576d6cc175f07044e98a43a74bbaf0190d9a353fc5cd0c3de`, MANIFEST.json `cf7a378d4d90c5d1ef84183692fb00e9c3ba5adac722a5a469ef6a3bf9eb7663`) and `…-amendment-f1b-v2/` (AMENDMENT.md `b84d2b3e280a77cb2fc0b4989735e9ef563ea6e9b430022721ca4156d8b49691`, inventory.json `071307ea6f13a2345ed31380563ad57f5e6aa1c8267d7ed44f2aa970a5a963af`, MANIFEST.json `eaacc836a846d7e0fc8ad67aad829e4ec15f8bf689331fb2176d1244382391c0`). v2 supersedes v1 with disclosure corrections from the objectives and mathematics reviews; every driver-bound field is byte-identical. The harness bound v2.
- A: F1b.1 expected target `/hypotheses` → `/binding`, labelled coupled derived-claim refusal coverage; the original row is preserved verbatim. B: new F1b.2, expected exit 3, `SCHEMA_INVALID`, stage 2, `/hypotheses`, empty stdout, no publication; label isolated model hypothesis-count bound, first refusal only.
- F1b.2 packet (`WS/inputs/F1b.2/selection`, binding `WS/metadata/binding-F1b.2-selection.json` `b4c3b7904eb8c6b5f7a3cc2c0665e47fe93ec00914dcf298c1fb6b7d785b3002`): the two state_hold claims and eight dependents removed; request `c0ea4152c7ef2d1a25749b405ed45337bafe22f05217f203c671fe8a969fff56` (2,303 B) then authority `6e0c5ce6aa9460f00f1b6be2cbc7929ceb7bc684e43faaceb79cb5b9cae5f554` (577 B); 27 objects, 104,889 B; closure closed (28 reachable, none missing or unreferenced); exactly one static schema violation (model `/hypotheses`, maxItems); first invalid record under the resolver's FIFO order is the model. Static predictions (system `jsonschema` 4.26.0, reimplemented traversal) were independently reproduced by a mathematical emulation including stage 1 and 3 checks. Control: FX1.1 (passed in launch 1).
- Pre-launch record `WS/reports/continuation-prelaunch.json` `4d6de849d41a7dd2afd68a29170b2416a39218c77bc7d032cabbc2b3dfe8e4fb`: harness hashes, schedule (112 entries, completed 128 not repeated), capacity and assumptions.

## 3. Execution (top-level launch 2, L1 continuation)

Driver `WS/metadata/continuation-driver.py` `25d73d4e216fe7f3e527072498c4a14393d73428ced4fed212ade9cb0c282f7f`, derived from the frozen driver by asserted text edits (diff retained); supervisor `d298c3bc28e9caea27b47b35cce65ebb1a23d095d0e3af2bdfc4fe994a694c18`; approved interpreter `47f615b1…`; memory group 1 GiB, peak 316,899,328 B, failcnt 0, empty afterwards. Reconstruction of launch-1 state (FX1, F1b, UN1) was byte-equal to the retained packets.

| Attempt | Result |
|---|---|
| F1b.1.a2 (A) | **pass**: exit 3, `{"code":"SCHEMA_INVALID","exit_class":3,"stage":2,"target":"/binding"}`, no bundle |
| F1b.2 (B) | **pass**: exit 3, `{…,"target":"/hypotheses"}`, no bundle |
| original F1b.1 (launch 1) | failure retained unchanged, consumed |
| F2b.1, F4a.1, F4b.1 | pass |
| F5a.1 | **stopped**: application exit 0, empty stderr, nine-file bundle published; harness oracle assertion failed |

L2 was not launched. Supervisor elapsed 25.759 s (cumulative L1 606.917 s; the driver-internal figure is 606.657 s). Records: `WS/reports/L1-continuation-summary.json` `2eae49ef0cda62cb35d6ebcdab001107912503c948e0eaa689c1ccc0184cec0b`, `supervisor-continuation.json` `189671f5d1690213046e3331e06e0ad0e688c19cfc43ed1e83be61157241644d`, `continuation-closeout.json` `944d39d17e1a16b2ba26e82b298b56a45080b94c29ace58b1256f863d119b36a`, `continuation-closeout.md` `199e83a624511728d9c49469d5e12579d2c6c776e16088bc44c654c9b6395184`.

## 4. F5a.1 attribution (read-only; `WS/reports/continuation-f5a-attribution.json` `4b9e267e1d64d7741fd0e79ee96be60d9bd998dae31c3e32d72e89723ec31b6b`)

CONTRACT v4 §3 defines the ideal predicted set as `[baseline − b_suspect.hi + b_ref.lo, baseline − b_suspect.lo + b_ref.hi]`; `checked_derivation.py:81-82` implements it and the retained `derivation.json` equals it exactly. The frozen launch-1 oracle (`driver.py:459`, copied verbatim into the continuation) uses `[baseline − b_ref.hi − b_suspect.hi, baseline − b_ref.lo − b_suspect.lo]`. Both coincide for `b_ref = [0,0]` and the symmetric OB4 `[−1/2, 1/2]`, which covers every selection case executed before; F5a (`b_ref = [0, 1/1000000]`) is the first asymmetric case reached. The manifest's own F9a clarification holds only under the contract convention. Classification: **harness oracle defect in the frozen driver; not an application discrepancy; not a manifest expectation mismatch** (manifest expects F5a admitted). F9a.1 would fail the same assertion. Correcting the oracle is an oracle change, outside the authorization; nothing was retried or repaired.

## 5. Coverage and cumulative accounting

| Item | Value |
|---|---|
| Matrix/control coverage passed | launch 1: 128 matrix; continuation: 5 matrix (incl. the two corrected F1b cases); internal 0 of 4; static 0 of 2 |
| Unexecuted | 100 CLI (F5b.1 … DL5.1, incl. SUP1.1 and 17 controls), 4 internal calls, 2 static checks; F3b/DG1 remain disclosed limits |
| CLI attempts | 135 cumulative = 129 + 6; authorized ceiling 235 (233 base + 2 owner-authorized); frozen generic maximum 241 |
| Combined CLI + internal | 135 of 245; retry slots 0 of 8 (none consumed by the continuation) |
| Top-level launches | 2 of 4 (L1 twice); pytest 0 of 2 |
| Helper upper bound | 953 of 10,000 |
| L1 wall | 606.917 s of 14,400 |
| Storage after closeout (workspace) | 4,242 files, 475 dirs, 30,409,036 B logical, 47,558,656 B allocated (st_blocks); plus seven external coexistence files 77,546 B; ceilings 48,000 / 1,500 / 805,306,368 / 1,073,741,824 |
| Preservation | 60 protected entries and 2,625 input commitments rechecked, 0 drift; launch-1 records unchanged; Gate 1 untouched |

## 6. Disclosures

- The frozen plan's document-retention scope (three files, zero directories) is exceeded by the owner-instructed packages: two new untracked directories, six files (bytes within the 1 MiB cap); this report adds a seventh untracked file. Owner may confirm or narrow.
- Harness review history: a first driver generation (`449c396f…`) was deleted before any launch after self-review found a branch defect; the v1-bound generation (`f3765f30…`) was retired by renaming after a code review found a Critical counter-scoping defect, which was fixed and re-verified before launch; a transient `__pycache__` from a compile check was removed from `WS/metadata`. All launches used only the final harness.
- Snapshot labels: driver usage snapshots are point-in-time and exclude files written afterwards; the closeout's external allocated figure (94,208 B) differs from a stat-blocks sum (114,688 B) by method only.
- Static checks used the system `python3` for `jsonschema`, not the approved interpreter; the application never ran outside the authorized launch.
- No production repair, full suite, staging, commit, cleanup, remote operation or publication occurred. Gate 2 remains incomplete and unqualified; acceptance is a separate owner decision.

## 7. Owner decisions required

1. Disposition of the frozen oracle's `b_ref` sign (harness defect): a successor oracle correction would need its own authorization and a new launch allowance; the stopped continuation cannot be resumed (one-shot locks).
2. Whether the two corrected F1b attempts are accepted as the F1b coverage.
3. Confirmation or narrowing of the document-retention count excess.

END OF GATE 2 CONTINUATION STOP REPORT
