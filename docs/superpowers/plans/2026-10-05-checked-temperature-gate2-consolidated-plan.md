# Checked temperature: consolidated Gate 2 proposal

2026-10-05. **Documentation only; Gate 2 is not authorized or executed.** This plan qualifies the existing bounded application against v4, C1 and C2. It does not qualify authenticated chronology, physical acquisition, causal diagnosis, adoption, reranking, deployment or release. Gate 1 consumption remains separate. Previous proposals, frozen packages, failures and unrelated modifications remain intact.

The [canonical manifest](2026-10-05-checked-temperature-gate2-manifest.json) is the exact case/command inventory and static preservation index. Its SHA-256 is `7f6a236f0f07cdc6c51e89830632bad8e045cdf7d52aec0c88834158a82a9d09` (419,851 bytes). Serialization is UTF-8, sorted keys, compact JSON, no BOM or trailing newline, and no self-hash. Manifest fields `case_inventory`, `invocations`, `support_invocations`, `control_invocations`, `internal_controls` and `static_only_controls` distinguish the different kinds of work. Every CLI row supplies argv, pins, input paths, expected exit/diagnostic/result and comparison method. Concrete future build/input digests remain deliberately ungenerated; this is an execution specification, not a ready-made runtime corpus.

## Verified checkpoint and preserved attribution

Read-only Git inspection verified HEAD **`4d6ab13c46642e9771199dced7d312ac94bbbb2f`**. Its committed additions are the real-build test and report below; both working files equal the committed bytes. The application/backend paths have no reported modifications. The unrelated modified `.gitignore` and bounded pytest runner, Git index, and retained inputs were hashed for preservation. No identity was generated and **no execution evidence exists at 4d6ab13**.

| Record | SHA-256 | Meaning |
|---|---|---|
| [Committed real-build test](../../../tests/checked_temperature/test_real_build_success.py) | `439fab0a5827691fe1b8b0daf4fe563eefa5b61996423cf46d4bea7b55ca2bab` | 10,862 bytes; source committed at this checkpoint, execution attributed below |
| [Committed real-build report](../reports/2026-10-05-checked-temperature-real-build-success-path.md) | `63dd13e11374d415068cc3c85808f7f1e1249e2e30f5f42262ab562269a7a905` | 7,995 bytes; launch 19, six tests passing, seven application CLI commands including the refused unpermitted-build twin |
| [Separate Gate 1 owner acceptance](../reports/2026-10-05-checked-temperature-gate1-owner-acceptance.md) | `e47286d1bac47b66a36e82c6e819e77bdc2b31233322242f53e424723fdb9c52` | 3,056 bytes; untracked and absent from HEAD; accepts implementation `8414f4d5f70a774b5c9cef1da82ce4ff55fc1cf8`, not a new execution at HEAD |

Launch 19's actual maintained build digest is **`d81acac6f40f97670c23d08df15b3d1f568df5433bdb8ac3b55961f33d27f23c`**, with checkpoint **`8414f4d5f70a774b5c9cef1da82ce4ff55fc1cf8`**. All four retained launch-19 selection/reassessment evaluation/replay bundles have matching manifest member digests and that build attribution. Their manifest hashes and individual member measurements are in `retained.launch19_bundle_members`.

Historical launch failures 01, 02, 05, 11 and 13 and launch 07's legacy identity failures remain attributed to those attempts. Launch 17 superseded the latter result without erasing it. Test-double evidence from launches 01–16 and 18 remains test-double evidence; launch 17 is the recorded clean legacy run. The acceptance records 19/40 Gate 1 launches. None of its unused launches, storage or repairs transfers to Gate 2.

## Contract reconciliation and recount

The governing inputs are [v4](../specs/2026-10-04-checked-temperature-contract-preparation-v4/CONTRACT.md), its [amendment map](../specs/2026-10-04-checked-temperature-contract-preparation-v4/AMENDMENTS.md), [C1](../specs/2026-10-05-checked-temperature-contract-amendment-c1/AMENDMENT.md) and [C2](../specs/2026-10-05-checked-temperature-contract-amendment-c2/AMENDMENT.md). All members of their manifests were hashed and size-checked read-only. The three package manifest hashes are respectively `9e0afa328c3281fd468be21911f7840a74a35cdafd616b3f79605eaebd5df529`, `791b4035807ce032f7852447df0e0b7d9324c8cb90d52bc8a1b6ebac42ab9d1a`, and `6252a2da6058b443db070954e7bf2a2ae075aba652ce6b09cabc0eb1b323bec6`.

| Recount stage | Cases/entries | CLI slots |
|---|---:|---:|
| v4, recounted from case arrays | 135 | 217 |
| C1 additional entries | 9 | 11 |
| C2 entries, before reconciliation | 8 | 10 |
| C2 repeats TC1, TC2a and TC5b; five new entries remain | 5 new | 5 new |
| Merged source catalogue | 149 unique IDs | 233 |
| Executable matrix after explicit sharing, splitting and internal-only exclusions | 138 constructions | **215** |
| RE4 prerequisite selection, separately counted | 1 support construction | 1 |
| Resource/delivery controls, separate from matrix | 11 groups | 17 |
| Proposed application CLI total | — | **233** |
| Internal API/fault calls, separately labelled | 4 | **4 calls** |
| Fixed-decoder data checks, no application invocation | 2 | **0** |

The merged catalogue is a historical obligation index, not the executable count. v4 retains 103 original expectations, amends F12b and adds 31 cases. C1 adds nine case IDs. C2 amends TC5b's formerly unresolved/accepted finished-time-only substitution to refusal because receipt remains outside the window; TC1 and TC2a are restatements, not extra commands. C2 adds RC1–RC4, with RC3a/RC3b distinct. The manifest preserves the prior entries/observations in `reconciliation.history_overlays` and superseded expectations. F12b's v3 resource refusal is superseded by v4 schema refusal; F12c covers the captured-count refusal.

Sharing is explicit: F1a/F2a/F3a use FX1; EO1/RE1/TC1/AP1 use UN1; CL1 uses UN1's standalone verify/replay; CD2 uses IN1; RC1 uses TC5b. F8b becomes two invocations (hi 50.000001 and lo 0). TC6 becomes baseline reuse (shared with RE3) and a separate occurrence-reuse invocation. Identical normalized bindings are mandatory for an alias; merely similar outcomes cannot justify sharing. These changes add two compound-case slots, remove eighteen shared slots and remove two non-CLI obligations: `233 + 2 − 18 − 2 = 215`.

F3b cannot inject an alternative decoder through the current public CLI. Its two alternatives are data-only checks against the exact edition; neither provides fresh executable refusal evidence. DG1's dirty/uncommitted-build scenario cannot run against the proposed clean checkpoint without a separately authorized checkout/source manipulation. IC1 tests provider-failure propagation internally, with a disclosed substituted provider; it does **not** qualify DG1's original real-process scenario. These are explicit remaining coverage limits, not passed matrix negatives. No arbitrary decoder/model ingestion or dirty checkout is proposed to conceal them.

| Command | Matrix | Support/controls | Total |
|---|---:|---:|---:|
| checked-selection-evaluate | 73 | 15 | 88 |
| checked-selection-verify | 34 | 2 | 36 |
| checked-selection-replay | 30 | 0 | 30 |
| checked-reassessment-evaluate | 53 | 1 | 54 |
| checked-reassessment-verify | 16 | 0 | 16 |
| checked-reassessment-replay | 9 | 0 | 9 |
| **Total** | **215** | **18** | **233** |

## Candidate, commands and future binding

The proposed candidate is current checkpoint 4d6ab13 in this existing repository, used read-only. Reuse the [Gate 1 approved environment](../reports/2026-10-04-checked-temperature-gate1-owner-approval.md): `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python`, recorded CPython 3.13.11, executable hash `47f615b1be25c94e9304ccd9339f9a8ef21d2194fca32643c441fb2dad290264`, and exact ten-distribution dependency lock hash `7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817`. Runtime availability/installed artifacts are unprobed in this preparation. No environment installation, backend change, clone or worktree is proposed.

Future L1 starts with the maintained real identity route, once, inside its reservation, then each command uses the maintained provider. The current candidate digest is unknown until then: checkpoint binding means launch 19's digest cannot simply be reused. Retain the new build record, environment/source commitments, preparation manifest hash, driver/oracle hashes and all concrete packet bindings in a new binding record under the proposed workspace. Never monkeypatch a permissive build into an ordinary matrix case.

Changing permitted-build entries changes the policy digest, model/request dependencies where applicable, request digest, authority target/digest, external pins and later execution/evidence/prior bindings. Rebuild these **new test packets** in dependency order. The source edition, calculator, frozen expectations and historical build records remain unchanged. Reassessment R commits its new prior manifest; X commits R and its exact occurrence, plan, context and acquisition. Existing public evidence can be reused only where all real bindings remain valid. Otherwise assemble a legal bounded synthetic fixture under the new inputs and retain its provenance; never alter old bundles or move old positive timestamps merely to obtain admission. Input-assembly failure stops. Accepting these prebuilt public records still leaves the physical acquisition producer gap.

For every row, substitute retained external request/authority pins, not pins inferred from the bundle being checked. Typical argv forms (full per-case forms are in the manifest):

```text
{PY} -m applications.bounded_decision_workflow checked-selection-evaluate
  --expected-request-pin {R} --expected-authority-pin {A}
  --request {request.json} --objects-dir {objects} --output-dir {NEW}
{PY} -m applications.bounded_decision_workflow checked-reassessment-evaluate
  --expected-request-pin {R} --expected-authority-pin {A}
  --request {request.json} --objects-dir {objects} --prior-bundle {PINNED_PRIOR}
  --output-dir {NEW}
{PY} -m applications.bounded_decision_workflow checked-{selection,reassessment}-verify
  --expected-request-pin {R} --expected-authority-pin {A} --bundle {BUNDLE}
{PY} -m applications.bounded_decision_workflow checked-{selection,reassessment}-replay
  --expected-request-pin {R} --expected-authority-pin {A}
  --bundle {BUNDLE} --output-dir {NEW}
```

IN1 additionally supplies the altered cached derivation; DG2 deliberately omits external pins. FX1 precedes its consumers; SUP1 precedes RE4; OB4's selection precedes its reassessment; WD1 precedes WD2; SC1 replay precedes IN10's mismatching-prior test; RB4.1 precedes RB4.2. Mutation copies precede their consumers. No unlisted application setup command is permitted. SUP1 is explicitly counted because RE4 must reach the instrument-evidence check after its internally consistent substituted plan; it cannot consume ordinary FX1. Original retained bundles are never mutated.

## Obligations and comparisons

The manifest maps each individual obligation to concrete command templates, source input recipes/parameters, prior dependencies, external commitment slots, expected diagnostic code/stage/exit/target and result predicates. Before execution, the future binding resolves every digest placeholder and commits every packet file's path, size and SHA-256, including cached and mutated comparison inputs. Freeze that mapping before each dependency's first consumer; no unresolved slot may reach a command. These are late-bound identities, not discretion to change expected results.

| Obligation family | Exact inventory references | Comparison |
|---|---|---|
| Fixed calculations, decoder branches, offset/observation uncertainty | FX1, SC1, UN1/3/4, LB1, HW0/5/5p, OB2–4, F8/F9/T2 | Independent rational/set oracle; exact intervals, permitted/excluded branches and score domain; observation uncertainty applied only in reassessment |
| Plan capture/change, result and execution joins | PM1, PS1–5, PB1, EO2–13, RE2–10, TC/RC | Exact bound model/plan/context/instrument/occurrence/time/value; intended first refusal or admitted conditional result |
| Conditions, evidence aggregation and policy | CB1–3, AG1–14, DC1–3, PO1–5, WD1/2, AV1–3 | Declared truth, review/evidence qualification and condition assessment checked separately; opposed/conflicting block; A1-permitted unresolved assumptions remain visible |
| Derivation versus downstream integrity | IN1–11, CD1/3 | Fresh calculation comparison, external pins, permitted builds; altered cached/rehashed derivation refused; altered score distinguishes verify from replay |
| Kind/closure/schema/limits/edition | F/CL/EC/LM cases, F12c, DG2 | Exact refusal precedence, code/stage/expanded target; bounded encoded carriage and closure reachability |
| Capture-count and publication controls | RB1–6, DL1–5, IC1, PF1–3, F3b data checks | Separately labelled boundaries/faults with their limited claims |

An evaluate/replay success has exit 0, empty stderr, one canonical receipt plus LF, and a nine-file bundle with manifest/member integrity. Withheld selection, ineligible baseline and blocked/incomplete applicability may be successful completed outcomes; absence of ranking does not imply refusal. Refusals compare exact `ct.diagnostic.v1` code, stage, exit class and expanded target, empty stdout and one canonical stderr diagnostic plus LF. Evaluate/replay refuses without successful publication; verifier refusals preserve source bytes. A wrong earlier refusal is a failure even if its exit class matches.

The arithmetic/branch oracle must use standalone integer/rational enumeration, without importing the repository derivation/ranking/reassessment calculator. It shares declared premises, not independent physical knowledge. It audits evidence/claim joins separately. E.g. F9a with b_ref `[0,10]` is admitted but changes the ranking to a T1/T2 tie; the phrase “checked as SC1” does not license copying SC1's score. BE1 preserves the catalogue's public baseline 60.2/model 60.1 direction; the retained reciprocal test-double is not substituted silently. Duplicate-T1 F2b removes unrelated T2 objects to reach its semantic duplicate check.

Verification independently recalculates derivation and applicability/policy, checks committed inputs and required output metadata, and reports `downstream_result_not_replayed`. Reassessment verification also checks carried prior material. It does not establish score/compatibility equality: IN3's correctly rehashed altered score can pass verification with this explicit limitation. IN2's altered derivation and IN5's false operational metadata must fail.

Independent replay runs in a fresh command process with only the bundle and external pins, reconstructs its closed inputs, freshly evaluates, and compares semantic result/trace/derivation/applicability records. Its invocation/replay-of fields are compared by role rather than demanding byte equality with the original invocation. IN4's altered score fails downstream comparison. Reassessment replay requires no external prior directory: UN1/WD2 test self-contained prior carriage. Replay requires the exact recorded build; permitted-but-different builds are not legal substitutes. An unavailable historical build is disclosed as unavailable, never replayed under a lookalike. Verification's permitted-current/permitted-recorded checks and replay's exact-build requirement remain distinct.

TC/RC exercise declared synthetic temporal joins, including closed-window boundaries and C2's start ≤ receipt ≤ finish rule. Receipt and finish must both lie in the T1 window. RC3b can accept a coherent changed finish within the window; this proves consistency checking, not authenticity. Unique conditional compatibility still does not confirm actual cause, issue execution permission or adopt a hypothesis. No NM/NR history is silently upgraded.

## Controls, launch boundary and stops

L1 is one new bounded driver process, including finite input assembly, binding, the 215 matrix invocations, SUP1, 17 control CLI invocations, four internal calls, two decoder data checks and twelve retained mutation copies. Its driver/oracle does not exist as an executed qualification artifact yet. Future authoring is harness-only within the workspace; application/test/contract source changes are excluded. Gate 2 reports must separate matrix, support, CLI controls, injected controls and uncovered original obligations.

RB1 checks exact 38-object FX1 admission versus cap 37 refusal; RB2 checks ten versus nine derivation cells (exact ten shared with FX1); RB3 checks a two-revision successor against permitted four versus one; RB4 first creates a prior with retained-selection cap 1,000, then refuses its reassessment; RB5 separately tightens hypotheses/procedures/outcomes/fractional digits; RB6 checks exact trace 8/rational operations 34, with LM6/7 testing one lower. Fresh policies are rebound, not inserted into pinned old requests. Ordinary F/LM boundary cases stay in the matrix and are not recounted as controls.

DL1 refuses an existing output directory without overwrite; DL2 refuses a missing output parent; DL3 refuses an absent bundle; DL4 verifies an eight-file copy lacking its manifest; DL5 closes the stdout reader before launch and expects exit 7 after complete publication, with no receipt promoted to success. PF1 injects a scoped fourth-file selection write failure; PF2 a selection file-fsync failure before the manifest; PF3 a reassessment directory-fsync failure after the manifest. Each expects retention exit 6 and retains every partial/complete file with its failed-attempt label. Injection affects only the named publication operation, in memory, never executable source or build generation. IC1's substituted unavailable provider is the sole build double and is labelled internal-only. These fault checks do not establish crash/power-loss durability or another filesystem's behavior.

L2 is one targeted pytest process selecting **only** the five paths in `legacy_scope`: ranking slice4, support qualification slice3, measurement contracts/closure, reassessment assessment and reassessment admission. Proposed invocation is the approved Python with `-m pytest -o addopts='' -p no:cacheprovider -q`, those five explicit paths, and a fresh `--basetemp` under L2; use `PYTHONDONTWRITEBYTECODE=1` for L1/L2. Do not use the unrelated modified bounded runner. [v3 PLAN, Gate 2](../specs/2026-10-04-checked-temperature-contract-preparation-v3/PLAN.md) specifies these two launches and explicitly excludes full-suite/release qualification; [v4 AMENDMENTS](../specs/2026-10-04-checked-temperature-contract-preparation-v4/AMENDMENTS.md) defers G2 resizing. No governing clause requires the full suite. The corpus-writing reassessment delivery test remains excluded.

Base launch count is **2 top-level processes**, **233 CLI children**, **4 internal calls**, **1 pytest launch**. Proposed maxima are **4 top-level processes**, **245 combined CLI/internal attempts** and **2 pytest launches**. Eight infrastructure-only extra child attempts share one allowance; the CLI maximum 241 and internal maximum 12 cannot both be added. Two infrastructure relaunches share the top-level allowance; no full matrix reset. At most 10,000 identity/Git helper subprocesses are separately counted across L1/L2; no arbitrary helper launches. Failed/interrupted attempts count and retain streams, metadata and partials. There is **no code/contract/expectation repair allowance**. Semantic/diagnostic failures stop for the owner, not retry-until-pass.

Before each child, reserve the maximum remaining input/output/stream/metadata footprint, then check usage before/after. Stop on checkpoint/protected-file drift, missing identity/environment/input pins, alias inequality, any unexpected outcome, out-of-root write, insufficient reservation, timeout/stream/memory/helper ceiling or incomplete publication. Stop L1 immediately on a failure and do not launch L2; L2 failure ends the campaign. Kill and reap the process group on a boundary failure; retain the aborted attempt and report actual overshoot if any. No ledger update, cleanup, overwrite, implicit continuation or borrowing from Gate 1 is allowed.

## Static sizing and proposed separate reservations

Measurements below are read-only logical file sizes; allocated sizes use `st_blocks × 512`, including directory blocks when stated. Directory inventories exclude the existing root; future reservation counts include the new root. Enumeration convention/time differences from historical report totals are not rewritten or interpreted as cleanup.

| Retained material measured now | Files | Dirs excluding root | Logical bytes | Allocated files + dirs |
|---|---:|---:|---:|---:|
| v4 package | 7 | 0 | 212,115 | In manifest |
| C1 package | 3 | 0 | 9,273 | In manifest |
| C2 package | 3 | 0 | 6,598 | In manifest |
| Complete retained Gate 1 workspace | 3,942 | 767 | **23,365,808** | **39,288,832** |
| Launch 17 | 293 | 21 | 2,447,421 | 3,448,832 |
| Launch 18 | 495 | 155 | 2,470,289 | 4,685,824 |
| Launch 19 | 218 | 47 | 1,816,167 | 2,707,456 |

Launch 19's selection evaluation/replay bundles are 201,455/201,535 bytes; reassessment evaluation/replay bundles are 409,107/409,187 bytes. Selection closure is 38 members, 111,083 decoded/154,459 encoded bytes; reassessment is 71 members, 264,270 decoded/364,019 encoded bytes. Retained selection object inputs are 111,083 bytes in 38 files; reassessment inputs 213,281 bytes in 63 files. These are historical measured examples, not predictions of the enlarged matrix. Many Gate 1 test-double cases were in-memory and have no retained concrete packet; the future corpus is not already complete. The manifest contains exact retained source/member hashes, package inventories and the Gate 1 content-inventory commitment.

Application caps remain separate from campaign reservations: object 196,608 bytes; selection/reassessment decoded closure 1,048,576/2,621,440; encoded closure 1,474,560/3,670,016; unique objects 192/400; complete bundles 2,097,152/4,194,304. String/depth/nodes/integer digits/fractional digits/review/trace/rational limits and captured tighter-policy cases are represented in the manifest. Input-reader limits must also be respected; do not construct a larger malformed file and call an earlier reader refusal the intended semantic pass.

Proposed engineering ceilings, **not measured runtime demand**:

| Reservation | Logical bytes | Allocated bytes | Files | Dirs incl. root | Wall deadline |
|---|---:|---:|---:|---:|---:|
| L1, all inputs/outputs/control failures/retries retained | 805,306,368 (768 MiB) | 1,073,741,824 (1 GiB) | 48,000 | 1,500 | 14,400 s |
| L2, separate targeted run including retry | 16,777,216 (16 MiB) | 20,971,520 (20 MiB) | 600 | 300 | 1,800 s |
| **Combined new runtime reservation** | **822,083,584 (784 MiB)** | **1,094,713,344 (1,044 MiB)** | **48,600** | **1,800** | **16,200 s** |

L1 arithmetic is intentionally conservative and independently recounted:

| Included component | Reserved bytes |
|---|---:|
| 88 selection input packets × (1,048,576 + 196,608), plus 54 reassessment packets × (2,621,440 + 196,608) | 261,750,784 |
| 76 completed selection bundles + 6 copies at 2 MiB; 24 reassessment bundles + 6 copies at 4 MiB | 297,795,584 |
| 233 CLI + 4 internal calls × 256 KiB joint stdout/stderr | 62,128,128 |
| Reports, metadata, driver, binding and indexes | 33,554,432 |
| Publication-fault partial outputs: two selection + one reassessment caps | 8,388,608 |
| Temporary packet/copy coexistence, one construction at a time | 16,777,216 |
| Eight infrastructure retry attempts, rounded to 8 MiB each | 67,108,864 |
| **Component sum / headroom within L1** | **747,503,616 / 57,802,752** |

The input-file estimate alone allows 88 × 205 + 54 × 405 = 39,910 files; bundles/copies add 1,008, ordinary streams 474, retries at most 3,312, leaving capacity for reports/indexes/partials under 48,000. Input packets, completed outputs, every failed partial, streams, binding/source commitments, usage snapshots, reports, driver/oracle and transient coexistence all count. Actual directory layout must fit 1,500, not rely on the prototype's directory count. At the total logical ceiling, a planning approximation adding one 4-KiB tail block per file and 8 KiB per directory gives 1,014,202,368 allocated bytes, below 1 GiB; allocation behavior is unmeasured and actual allocated usage still binds independently.

Each L1 attempt has a joint 256-KiB stream cap; L2 has 1 MiB joint streams across its attempts. Child timeout is 900 seconds, aggregate process-group memory ceiling 1 GiB for either launch, with cumulative wall limits above. CPU demand, peak RSS, free filesystem capacity and future packet sizes are unknown. Reuse an existing approved aggregate memory enforcement facility only if available; if an enforceable limit is unavailable, stop before application execution and seek separate provisioning authorization. No cgroup/controller creation or availability probe was performed here. The driver must bound stream reads, kill groups at deadlines and stop before allocation when worst-case reservation does not fit. These ceilings grant no performance claim.

## Workspace, provisioning and retention boundary

Propose one **new**, dedicated runtime root `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/ct-gate2-4d6ab13`, outside all existing corpora and ledgers. All future writes, including pytest cache/temp/bytecode overrides, binding, copied inputs, controls and repair attempts, must remain beneath it. No symlink output escape; every evaluation/replay destination is new. Its creation and writes require explicit future authorization, including filesystem permission outside this documentation workspace. The ext4 parent is recorded by Gate 1; its present availability and capacity are unprobed. Confirm it non-mutatingly after authorization; do not mount/provision another filesystem automatically.

Use the current checkout and existing approved environment; no checkout, worktree, dependency installation or mount is requested. If checkpoint, interpreter/distribution artifacts, filesystem or enforceable resource controls are unavailable, report the gap and request separately scoped provisioning. Earlier campaign provisioning is neither a requirement nor inherited permission. No backend extension is implied. Harness/input assembly is future execution preparation inside L1, not an implementation repair.

Retain **all** new runtime inputs, outputs, manifests, streams, reports, command argv/pins, identity records, driver/oracle, usage metadata, failures, copies and temporary coexistence in place. This reservation permits no deletion even after pass/failure. Any later retention reduction or cleanup is a separate owner decision. Keep existing Gate 1 material untouched; static reading of it incurs no new copied-workspace entitlement.

The exact proposed repository-document retention scope is only these three in-place files, separately capped at **1,048,576 logical / 4,194,304 allocated bytes, three files, zero new directories**:

1. `docs/superpowers/reports/2026-10-05-checked-temperature-gate1-owner-acceptance.md` — retain its current bytes/hash; remains untracked.
2. `docs/superpowers/plans/2026-10-05-checked-temperature-gate2-consolidated-plan.md` — this new proposal.
3. `docs/superpowers/plans/2026-10-05-checked-temperature-gate2-manifest.json` — this new canonical inventory.

No staging, commit, Git ignore change, ledger modification, old-artifact migration or remote retention is proposed. The committed real-build report/test and all other existing material retain their current status. The preparation manifest contains no plan self-digest; this document binds it, and the delivered digest binds this document without a circular hash dependency.

## Preparation checks performed

Disclosed execution was limited to read-only Git commands and source/document reads; standalone Python standard-library JSON parsing, SHA-256, file/directory `stat` enumeration, arithmetic, canonical new-document generation and static consistency/link checks. One draft static check used a wrong JSON package key and stopped with `KeyError`; it was corrected using explicit source paths. No repository imports, identity generation, test collection, pytest, application commands, runtime probes, synthetic experiments, launch-log entries or ledger mutations occurred. Checks of the finished files recount IDs/commands, compare source/protected hashes, verify canonical encoding and local links, and recheck HEAD. Only these two new Gate 2 documents were written.

## Consolidated owner decision request — no execution yet

Approve or amend **one Gate 2 scope**: current checkpoint 4d6ab13, existing recorded CPython environment, the manifest at the digest above, 138 matrix constructions/215 commands plus one SUP1 setup and 17 CLI controls (**233 CLI total**), four explicitly internal calls and two decoder data checks; twelve mutation copies; exactly the five named legacy files in L2. Accept the stated F3b/DG1 real-process coverage limitations, or defer those obligations to separately authorized work. No dirty checkout, arbitrary decoder route or full-suite expansion is included.

The requested ceilings are **two base/four maximum top-level launches**, **237 base/245 maximum CLI-plus-internal attempts**, **one base/two maximum pytest launches**, **eight shared infrastructure-only extra child attempts**, **10,000 identity/Git helper children**, **784 MiB logical/1,044 MiB allocated**, **48,600 files/1,800 directories**, **16,200 seconds cumulative wall time**, **900 seconds per child**, **1 GiB enforceable process-group memory**, and stream caps **256 KiB per L1 attempt / 1 MiB across L2**. L1/L2 subceilings and no-repair stop rules above apply independently; no Gate 1 reset/borrowing.

Authorize only the proposed new runtime root's creation/writes and bounded future harness/input assembly, conditional on the unchanged checkpoint and existing environment/filesystem/enforcement availability; authorize the exact three-file in-place document retention scope and all bounded runtime artifacts. If enforcement or provisioning is unavailable, stop and return for a separate decision. The genuinely unresolved choices are **whether to grant this execution/storage/retry scope and whether to accept the two explicit fresh real-process coverage exclusions**. No authority issuance, adoption, cleanup, commit or publication decision is requested. This preparation stops here.
