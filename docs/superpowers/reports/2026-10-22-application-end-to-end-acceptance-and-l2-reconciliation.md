# Scoped synthetic end-to-end acceptance and reconciliation with the frozen L2 plan

Date 2026-10-22. Preparation only.

- Nothing was executed, imported, tested, built, installed or committed.
- No Git, K or merge was run.
- **The L2 baseline is frozen and unchanged:**
  - packaging proposal `74a39d87586b50e91fb5862579f28c02f86c498a6fa69e02bfb97e487d059a1b`;
  - scope addendum `6bca403bf936cf47da0eea373af8b587578a4b995d2b6ffdd7cb48fb1b77425e`.
  Both were re-hashed before writing. This file is a new proposal alongside them.
- **Labels:** [SRC] source-confirmed; [OBJ] read now; [HIST] historical; [REC] recommendation;
  [OWNER] reserved to the owner; [est] estimate.

## 1. Scoped end-to-end acceptance (owner decision recorded here)

**Accepted claim:** one fresh synthetic development workflow completed **acquisition → handoff →
owner-authorized evaluation → workflow verification → replay**, under historical commit
`07055c6357a049dba4599b527a1ce261ec529a2c` and build
`0fc2cd251919ed1d47fc9476627c1beb6f486480d14d104016c1910cd6de4f31`.

It used:
- retained synthetic inputs, reused unchanged;
- freshly executed stages;
- an explicitly owner-approved evaluation authority A
  (`327895c8954061761e4f6a1c6bb5e6cb9ed7ddb909031499f680bd2011027186`).

**Not established:**
- input authoring;
- adoption (the result records `derived_not_adopted`);
- physical-world validity;
- L1 integration (the engine is pre-L1);
- portable installation or L2;
- enterprise readiness.

**Not repaired:** the 2026-10-13 pilot's FAILED/INCOMPLETE independent audit, which keeps its
original status.

**Unchanged:** no historical receipt is amended or relabelled. R1's 141 results and the scoped L1
acceptance keep their attribution, the three deferred cases stay deferred, and D-P is open.

## 2. Evidence linkage (independently read and hashed now) [OBJ]

| Record | SHA-256 (prefix) | Result |
|---|---|---|
| `ACQ/evidence/STATUS.json` | `2572ff28…` | Matches. Outcome `ACQUISITION_HANDOFF_COMPLETE_AWAITING_OWNER`, 97 of 97 checks true |
| `ACQ/evidence/OWNER-DECISION-PACKET.json` | `a0dcce71…` | Matches |
| M `ACQ/out/m/manifest.json` | `fe2d646e…` | Matches |
| H `ACQ/out/h/handoff.json` | `be4b996b…` | Matches |
| R `ACQ/out/h/objects/5f72989d…` | `5f72989d…` | Matches |
| `EVR/evidence/STATUS.json` | `324bc69d…` | Matches. Outcome PASS, 136 of 136 checks true |
| `EVR/evidence/RECEIPT.md` | `1cf73170…` | Matches |
| A `EVR/inputs/a/327895c8…` | `327895c8…` | Matches |
| B `EVR/out/b/bundle/manifest.json` | `e9f9e97f…` | Matches |
| F `EVR/out/b/workflow-receipt.json` | `607a25bd…` | Matches |
| Verification report `EVR/out/v/report.json` | `c5a2ae55…` | Matches |
| Replay manifest `EVR/out/r/manifest.json` | `d15f22fc…` | Matches |

`ACQ = …/test-workspaces/acq-handoff-07055c6-20261022-1`;
`EVR = …/test-workspaces/evr-07055c6-20261022-1`.

**Chain links read now:** F names `evaluation_authority` A, `handoff` H, `output_manifest` B,
`producer_manifest` M and `request` R.

**Supported by the retained STATUS checks** (not recomputed here):
- the expected synthetic result: 60.1 °C, interval [298/5, 303/5], H1
  `compatible_under_declared_model`, H2 `conditionally_incompatible`, `one_compatible`,
  `not_reassessed`, `derived_not_adopted`;
- verification against F;
- seven replay byte equalities, and `replay_of` = B.

**Limits:**
- Storage was sampled once per run. Helper and session overhead was not measured.
- Wall clock and uptime differed slightly in the runs (0.66 s here). The cause is unverified.
- Each run's receipt lists only the records the supervisor wrote before it.
- "All required checks passed" does not mean every operational quantity was measured.

## 3. Identity map: current L1 tree versus the historical clone [SRC]

**All five demonstrated commands reach build identity through a single provider:**
`checked_runtime.ExecutableBuild` (current tree, `checked_runtime.py:37–66`).
- `ExecutableBuild.wire()` calls `measurement_build.identity()` and wraps it as `ct.build.v1`.
- In the current tree, `measurement_build.identity()` has L1's installed branch
  (`measurement_build.py:22–26`, using `release_identity.present`/`verified_source`). In the
  historical clone (`172efff4…`) it is Git-only.
- No T1 module and no `checked_cli` path runs Git or another identity provider. Within the T1,
  checked and measurement modules, a grep for `subprocess` matches only
  `measurement_build.py:7, 19, 35` and an exception name at `checked_runtime.py:52`. Outside those
  modules it also matches `build.py` and `governed_build.py`.
- The Git-only providers are `build.identity()` (legacy S1–S7) and `governed_build.identity()`.
  **No demonstrated command uses them.**

| Command | Provider and call sites | Checkout (Git mode) | Installed (L1 mode) | Scenario build restrictions | Proposed change |
|---|---|---|---|---|---|
| `t1-simulation-run` | `t1_cli.py:169` `ExecutableBuild()` → `t1_records.py:261` `a.build.wire()`; prior verify through `checked_runtime.verify` (`t1_records.py:300–303`) | Requires a clean committed tree | Supported by L1 (verifies `app/` from the release record; no Git) | J `producer_build` == current build; build ∈ simulator policy producer list and captured `permitted_builds` (`t1_records.py:265–275`); prior bundle policy permits current build | **None to identity** |
| `t1-reassessment-prepare` | The same provider (`t1_workflow.prepare_handoff` → `simulation.verify` → `t1_records`) | As above | As above | As above | None |
| `t1-reassessment-evaluate` | The same, plus `checked_cli.execute` delegation (`_current_build`, `checked_runtime.py:916`); F records `checker_build` (`t1_workflow.py:206`) | As above | As above | As above, plus the bundle policy permits the current build | None |
| `t1-workflow-verify` | The same (`t1_workflow.py:238, 294`) | As above | As above | Producer and checker builds permitted | None |
| `checked-reassessment-replay` | `checked_cli.py:186` `ExecutableBuild()` → `_current_build` (`checked_runtime.py:996`) | As above | As above | Recorded and current permitted; **current == recorded** (`:1005–1008`) | None |

**Conclusion:** the identity work is already covered by L1 for this workflow. L1's acceptance
covers the installed-witness behaviour in a matched environment, so **no identity code change is
needed.**

**Three real gaps remain:**
- **(a) Deployment and startup:** the frozen L2 design (`deployment.py`, `release_check.py`,
  release tooling).
- **(b) Fixture compatibility** (section 4).
- **(c) Validation runs:** on a committed source and an installed release.

**Nothing weakens identity:** no dirty-tree suppression, no caller-asserted build and no
permitted-build bypass is proposed.

## 4. Fixture compatibility

### 4.1 Why the retained inputs cannot be reused

- Every changed byte under `applications/` or `backend/`, a different commit, or a different
  interpreter changes the build digest, because `nm.build` embeds the checkpoint, source manifest,
  interpreter executable hash and distributions.
- The retained inputs permit only `0fc2cd25…`, so they refuse on any L1/L2 build.
- The L2 release, with its own interpreter, has a digest that is **known only after the release is
  built**.
- The historical pass stays attributed to `07055c63` and `0fc2cd25` only.

### 4.2 The exact cascade

A read-only reference walk over the 69 retained objects (14 simulation, 30 request, prior closure)
found that **9 objects change by reference**, plus **one produced by the simulator** (the review finding, corrected below):

| Kind | Object | Why it changes |
|---|---|---|
| Embeds the build | `ct.policy.v1` `9bf140fb…` (`permitted_builds`; the captured policy) | Direct |
| Embeds the build | `ct.t1-simulator-policy.v1` `2342bbcb…` (producer and checker lists) | Direct |
| Embeds the build | `ct.t1-simulation-target.v1` J `11669422…` (`producer_build` and policy references) | Direct |
| Embeds the build | `ct.t1-simulation-permission.v1` G `d4cd11c6…` (scope `producer_build` and references) | Direct |
| References a changed object | Selection request P `f32c2ce2…` (policy) | Refers to the policy |
| References a changed object | Selection authority A0 `40ae3dcb…` (target P) | Refers to P |
| References a changed object | Conditional request R `5f72989d…` (policy, prior selection, execution target) | Refers to the policy and the regenerated selection |
| References the regenerated prior selection | Execution target X `38c7e3b2…` (`prior_selection` manifest and selection) | Refers to the regenerated prior bundle |
| References the regenerated prior selection | Execution authority E `408492e8…` (target X) | Refers to X |

**A tenth object depends on the simulator's own output.** The producer public evidence
`nm.evidence.v1` `686ecc43…` has an `id` embedding a **truncated J digest**
(`E-t1-11669422a04923…a922c30`, the first 60 hex characters). The fresh M emitted it byte-identically
as `out/m/evidence/public/evidence.json`, and R references it as `result.acquisition.public_evidence`.
Under J′ the simulator emits a new evidence′, so **R′ can only be rendered after acquisition on the
new build**. It is the only prefix-only dependency found in a 12-character prefix scan of all 69
objects.

The other 59 objects are reused unchanged.

**Two further outputs must be produced, not rendered:**
- the **prior selection bundle**, by the maintained `checked-selection-evaluate` under the new
  build, from P′ and A0′;
- a **fresh evaluation authority A′** for R′, after handoff, as for A.

### 4.3 Existing authoring is insufficient

- `t1-simulation-prepare` refuses with `SIM_INTERNAL_ERROR /incomplete/prepare-templates`
  (`t1_cli.py:69–70`).
- The pilot's five authoring helpers were report-local and imported test fixtures [HIST]. They are
  not maintained.
- So a small prerequisite is unavoidable.

### 4.4 Minimal prerequisite: a deterministic re-binding tool [REC; separate and bounded, not an authoring product]

**File:** `tools/fixtures/t1_rebind.py`. It is stdlib only, and sits outside `applications/` and
`backend/`, so it does not change the application identity.

**Stage 1:**

```text
t1_rebind.py stage1 --retained <pilot dir> --permitted-build <digest> [...] --attestations <owner json> --out <new dir>
```

- Renders candidate canonical bytes for policy′, P′ and A0′.
- **Mechanical rule:** replace `permitted_builds` with the given digests, then substitute old
  digests with new ones, in dependency order.
- Attestation `label` and `basis` text comes only from an owner-supplied JSON file. No retained
  "Gate 1 test fixture" text is carried into a new attested record.
- Writes `REBIND-REVIEW.json`, listing every changed field (old and new) and every new digest.

**Then:** the maintained `checked-selection-evaluate` produces B0′ from P′, A0′ and the unchanged
objects, under the target build.

**Stage 2:**

```text
t1_rebind.py stage2 --retained <pilot dir> --stage1 <dir> --prior-bundle <B0' dir> --permitted-build <digest> [...] --attestations <owner json> --out <dir>
```

- Renders simulator policy′, J′, X′ (new `prior_selection` references), E′ and G′, using the same
  rule and the same review file.

**Then:** the maintained `t1-simulation-run` produces M′, including evidence′.

**Stage 3:**

```text
t1_rebind.py stage3 --retained <pilot dir> --stage2 <dir> --producer-package <M' dir> --attestations <owner json> --out <dir>
```

- Renders R′, taking `result.acquisition.public_evidence` from M′'s actual
  `evidence/public/evidence.json`, plus the stage 1 and 2 substitutions.
- Substitution covers whole digests **and** digest prefixes, as in the evidence `id`.

**Boundaries:**
- The tool never writes approvals and never invokes the application.
- **Rendering bytes is technical serialization. Approving the attested records is substantive and
  owner-owned:**
  - the policy (its permitted builds are a policy-owner decision);
  - A0′, E′, G′ and later A′ (authority and permission issuers).
  The owner reviews exact bytes before each is used, as was done for A.

**Tests:** `tests/tools/test_t1_rebind.py`, using copies of the retained fixtures in a temporary
directory:
- determinism, and canonical form;
- `REBIND-REVIEW` completeness;
- refusal if any old digest **or any prefix of 12 or more hexadecimal characters** of an old digest remains in rendered output;
- unchanged objects left byte-identical;
- no fabricated attestation (refuses without owner text).

### 4.5 What the next milestone can claim

| Option | Input work needed | Claim |
|---|---|---|
| **A: L2 as frozen** | None | Installed **initialization only**, as in the scope addendum |
| **B: installed full workflow** | Option A, plus the re-binding tool, the release build digest, owner approvals (policy, P′/A0′, E′/G′/J′/R′, later A′), one `checked-selection-evaluate`, and the five commands, all on the installed release | The full chain from the installed release |

## 5. Implementation and validation map [REC]

### 5.1 Files

| File | Change | Note |
|---|---|---|
| L2 files (unchanged from the scope addendum §5.1): `deployment.py`, `release_check.py`, `tools/release/release_manifest.py`, `build_release.sh`, `install_release.sh`, their tests, the runbook | New | |
| `tools/fixtures/t1_rebind.py` | New | **Option B only** |
| `tests/tools/test_t1_rebind.py` | New | **Option B only** |
| Existing files | **No edits** | No identity change is needed (section 3) |

### 5.2 L1 test attribution

- Adding the L2 modules under `applications/` changes the tree, so all **20 L1 tests re-run** on
  the new commit, under the dev environment and under the release interpreter in staging.
- **These are new results.** The original L1 acceptance stays tied to its bytes.
- The re-binding tool, being outside `applications/`, does not change the tree.

### 5.3 Sequence

The order is adjusted for identity reasons: a workflow needs a committed or installed tree, and
inputs need the final build digest.

1. **Implement** the L2 files, and the re-binding tool for option B.
2. **Development tests:** the 20 L1 tests, the L2 tests and the re-binding tests. They all use
   temporary fixture repositories, so a dirty tree is fine.
3. **Release commit `C`** (a later commit grant). It must come **before** any workflow run,
   because the Git-mode provider refuses a dirty tree. The tested source-set digest equals the
   export of `C`.
4. **Staging build** on the reference host at `R_REL`. Run the L1 and L2 tests under the release
   interpreter, then `release_check` to obtain the **release `ct` build digest**. Inputs cannot be
   prepared before this digest exists.
5. **Option B input preparation:**
   1. stage-1 rendering, with permitted builds = the release digest;
   2. owner approval of policy′, P′ and A0′;
   3. `checked-selection-evaluate` on the staging install;
   4. stage-2 rendering;
   5. owner approval of E′, G′, J′, X′ and the simulator policy′;
   6. `t1-simulation-run` producing M′;
   7. stage-3 rendering of R′ from M′'s evidence′;
   8. owner approval of R′.
   This splits acquisition from the rest of step 6.
6. **Fresh workflow on the staging install:** handoff (consuming M′ and R′), owner A′, evaluation,
   verification and replay. Acquisition already ran in step 5.6. This uses the proven supervisor scripts, re-pinned. It is the "fresh
   workflow on the changed checkpoint", running in installed mode.
7. **Package:** checksum-only manifest. The inputs are **not** part of the release; they are
   transferred separately with their hashes.
8. **Fresh VM installation and validation:**
   - the L2 VM steps (initialization);
   - then, for option B, the same workflow on the VM. The same inputs apply only if the VM's `ct`
     digest equals staging's. `nm.build` records `platform.libc_ver()`, system and machine, the
     executable hash and the distribution file hashes, so this requires identical release bytes, the
     same prefix and the same glibc version string (noble ships 2.39).
   - V4 must compare the VM digest with the staging digest before any re-bound input is used.
   - If acquisition is repeated on the VM, its evidence must be identical, or R′ must be re-rendered
     and re-approved.
   - Step 4's tests must not run in the packaged prefix; keep the scope addendum's manifest check
     before and after them.

**Governance:**
- **K and R3** govern the historical K judge and launcher regressions, so they are not required.
- **The rule "K precedes every commit"** (K amendment proposal §5) was suspended by OD-K2 "for
  portability work only", but OD-K2 grants no commit authority. Whether that suspension covers
  commit `C` needs explicit owner confirmation.

## 6. Decision table

| Item | Status |
|---|---|
| End-to-end claim | **Accepted** (section 1): scoped synthetic development chain on `07055c63` and `0fc2cd25` |
| Frozen L2 decisions still applicable | Packaging, installation, initialization adapter, interpreter build, checksum integrity, VM design (proposal `74a39d87…` and addendum `6bca403b…`). OD-L2-A (`core_pattern` withdrawal) and OD-L2-B (digest channel) are still open |
| Integration scope | **No identity code change.** L2 files as frozen. The workflow runs in installed mode through L1 |
| Input prerequisite | **Option B only:** the `t1_rebind` tool (three stages; renders candidates; never approves), plus one maintained `checked-selection-evaluate`. R′ is rendered after acquisition |
| Material owner decisions | **(1)** Next milestone: option A (initialization) or B (installed full workflow). **(2)** For option B, approve the re-binding tool as a bounded prerequisite, not an authoring product. **(3)** For option B, the policy decision on permitted build digests, and who approves the attested records and their texts. **(4)** Whether OD-K2's suspension covers commit `C`. **(5)** OD-L2-A and OD-L2-B |
| Later grants | Implementation; development test run; commit `C`; reference build host; staging runs; per-object input approvals; VM provisioning; each validation execution |

## 7. Focused review

**Reviewer:** one focused, independent `code-reviewer` subagent.

**Restrictions it worked under:** read-only; one `sha256sum` of the fresh producer evidence; no
writes.

**Final text reviewed:** yes, the draft as written (16,115 B).

| Area | Result |
|---|---|
| Section 3, identity | **Correct.** All five commands use `ExecutableBuild` → `measurement_build.identity()`, with L1's installed branch; every citation is correct; no T1 or checked module uses `build` or `governed_build`. "No identity code change, nothing weakened" holds |
| Section 4 spot-checks | Hold: X references the prior manifest and selection; E targets X; R references the policy, prior outputs and X; the build digest appears only in the policy, simulator policy, J and G. A0 targeting P was confirmed by me from the decoded closure |

**Findings and dispositions:**

| Severity | Finding | Disposition |
|---|---|---|
| **Major** | The cascade missed the producer evidence `686ecc43…`, whose `id` embeds a truncated J digest. R references it, so R′ depends on simulator output and cannot be rendered in stage 2 | **Fixed:** a 10th object; a new stage 3 after `t1-simulation-run`; prefix substitution; a prefix-aware leftover test; sequence 5.3 updated. I re-ran a 12-character prefix scan of all 69 objects, and this was the only prefix-only dependency |
| Low | The `subprocess` grep statement was too broad | **Fixed** |
| Low | Staging/VM digest equality also needs the same glibc version string | **Fixed:** stated, with a V4 comparison before inputs are used |
| Low | Tests under the release interpreter could write `.pyc` files into the packaged prefix | **Fixed:** the manifest check before and after is kept |

**Not verified:** truncated digests shorter than 12 characters; run-time behaviour.

These fixes were not re-reviewed.

## 8. Accounting

| Item | Grant | Notes |
|---|---|---|
| Files | 1 | This file only |
| Directories | 0 | |
| Logical bytes | At most 131,072 | Charged against the unreserved preparation-byte balance |
| Allocated bytes | At most 147,456 | Same balance |

- **Balance before:** 11,932,838 / 26,451,968.
- **Balance after:** **11,801,766 / 26,304,512**.
- **Final size and SHA-256:** reported in chat, so this file contains no self-hash.

**How it was written:** exclusive creation by a standalone writer reading stdin. Later edits were
made only inside this unsealed file.

**Read-only actions:**
- hashes of the named evidence and of both L2 documents;
- source grep and reads in the current tree and the clone;
- plain-data reference walks over the retained fixtures.

**Not done:** no execution, test, import, build, installation, Git, checkout, K, commit or merge.

**Host and session scope:** separate, not charged here, and not zero.

END RECONCILIATION
