# C05 PID successor checkpoint and genuine build capture receipt

The sealed successor ran once and the outer process exited **0**. Admission passed, one isolated checkpoint was verified, one canonical build identity was captured, and runtime finalization completed in 73.37 seconds. The terminal record reports `checkpoint_verified=1 build_verified=1`.

## Authorization and admission

- The successor manifest matched 381 bytes and SHA-256 `19fcf3bd83924fe7ad97624fa1df7f3a998357831af65ef5894b132c9272fbc0`. All four exact members matched. The invocation separately matched 40,651 bytes and SHA-256 `6946a406d3e5fff10347c8de7ff0a3b3dc5d9c8ed16e705cc0f466ed6cc2a539`. The preflight matched all 11 external bindings, the three anchored manifests and their 10 members, the protected checkout and registrations, the 17 postimages and seven preimages, the 651 retained source records and projected provider inputs. It verified source, parent-object availability, tool and environment pins, and the authorized destination names. An independent preflight capacity helper raised an API error after the input checks. A separate read of capacity and destination absence completed successfully before dispatch.
- At 2026-11-21T06:13:51.373+00:00, the authorized worktree, runtime/evidence root and outer receipt were absent, as were the target ref namespace, target locks and worktree registration slot. Free space then was 861,698,572,288 bytes on ext4 and 978,223,026,176 bytes on the repository volume. The later sealed rechecks governed admission and first write.
- The sealed baseline verified 17 postimages, two contract pins, 636 matching component records and all 198 provider inputs totaling 2,315,373 bytes. It captured working membership before T0. Bulk admission checked 2,620 parent objects and required the original-state, historical and working comparisons to pass again. The immediate and fast ref checks both exited 0. The first-write clock was recorded 24.79 seconds after immediate entry and 162.55 seconds after T0.

## Phase timing and exits

Elapsed values below use the invocation's uptime clock. UTC stamps and the controller's receipt times are separately observed.

| Phase | UTC observation | Elapsed and result |
|---|---|---|
| Baseline | 06:14:08.187836952 to 06:16:20.018794521 on 21 November 2026 | 138.00 seconds from baseline clock 93372 to T0 107172, within 180 seconds. |
| Bulk admission | 06:16:20.018794521 to 06:18:31.511514186 | 137.76 seconds to immediate entry 120948, within 270 seconds. |
| Immediate recheck | 06:18:31.511514186 to the checkpoint stamp at 06:18:54.768364934 | 24.79 seconds to first-write clock 123427, within 30 seconds. Full admission used 162.55 of 300 seconds. |
| Checkpoint | 06:18:54.768364934 to pre-capture stamp at 06:20:06.991052405 | Approximately 75.48 seconds through the pre-capture observation, within 300 seconds. Pre-Git classification, worktree add and commit exited 0. |
| Capture | 06:20:06.991052405 to 06:20:08.634835650 | 1.65 seconds between stamps. Worker supervisor exit 0, reader exit 0 and operation exit 0. |
| Runtime finalization | 06:20:08.642690147 to terminal stamp at 06:21:17.134781656 | 73.37 seconds from finalization clock 131140 to 138477, within 120 seconds. Terminal status 0. |
| Outer controller | Submitted 2026-11-21T06:14:03.600Z. Observed exit 2026-11-21T06:21:19.927Z. | Outer exit 0. The outer watchdog did not expire. |

## Checkpoint

- Commit `f1e054cd4d5ed3e17c7c31e3532b16960e3c090c`, sole parent `0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3`, tree `a738cf4536726aff95b154baf0a41742e77012a4`.
- Branch `codex/c05-companion-native-v2`, full ref `refs/heads/codex/c05-companion-native-v2`, at worktree `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-src-20261120-01`. Worktree add first registered the branch at the exact parent. The verified transition to the commit is in the final ref classification.
- Staging had one dispatch. The commit had one dispatch with command-local `maintenance.auto=false` and `gc.auto=0`. The sealed checks verified the staged and committed tree against the complete projection, matched each approved blob to its source and worktree bytes, checked Git modes and worktree cleanliness, verified the commit's sole parent and exact metadata, and compared the effective isolated and original configuration. The retained name and raw stage records both agree with the authenticated TSV.
- Oracle `approved-checkpoint.tsv` is 4787 bytes at SHA-256 `04bcb4fa2c7c421ea2c759e44ca81bdabfac7ed21fb944970bbd41d1e67aeb1f`. Retained `staged-raw0` is 2608 bytes at `e6cb79d216da85949e1c63065fb8563223609cf9c8f202214cad72b494a6d2e6`. Retained `staged-names0` is 959 bytes at `0be470f3aaad690e3223b56ff9dbfa191ca056d700057ebf4c4cb2277bbc8533` and `paths0` is 925 bytes at `2d5233fdfefa4a00eeb726afcfd8d68a98b1911f8bb9e74d646d97c1e385812b`. The table is the verified seven modifications and ten additions.

| Change | Path | Parent mode and blob | Committed mode and blob |
|---|---|---|---|
| M | `applications/bounded_decision_workflow/checked_runtime.py` | `100644` `a8956736faa7f79cf48e839b97028ded724dd97b` | `100644` `c16b45e19ece20c301e819733385066ff9cd2389` |
| A | `applications/bounded_decision_workflow/t1_calibration_gate.py` | Absent | `100644` `07c465074292912f33a7c8aa7d0923b5aebb55a7` |
| A | `applications/bounded_decision_workflow/t1_calibration_schemas.json` | Absent | `100644` `3fc6c40dbfe96aad6a2bc1b2b6e3fc534cbabf2f` |
| A | `applications/bounded_decision_workflow/t1_calibration_schemas_v2.json` | Absent | `100644` `fec745ca2b78484d1c68945de6e6389fe39efa69` |
| M | `applications/bounded_decision_workflow/t1_cli.py` | `100644` `e75607512785c0d1db1440eef4fc878a8564ebd9` | `100644` `c413258eff16a63e9392f109040a65e8f925ee8c` |
| M | `applications/bounded_decision_workflow/t1_package.py` | `100644` `35f590b91f06a0748bc64ba825d6ef912fa52586` | `100644` `61f043c8dac2fe568b553a93d04118a19c9c1daf` |
| M | `applications/bounded_decision_workflow/t1_schemas.py` | `100644` `deb8e74e0be2ed11bba940413addac0408ed2524` | `100644` `bbd8c5dd9dfda14a37ee41e626b323e0508e389d` |
| M | `applications/bounded_decision_workflow/t1_workflow.py` | `100644` `024ba0c926e7dbba015ca2e3bc7a3f7195397b33` | `100644` `c39855dbc9d78415a6f9d05a1821e4c3f44d51aa` |
| A | `docs/superpowers/specs/2026-11-19-c05-companion-gate-v1/CONTRACT.md` | Absent | `100644` `fcc93baccc93c3ed15b2a26ab4151066934e3d5b` |
| A | `docs/superpowers/specs/2026-11-20-c05-companion-gate-v2/CONTRACT.md` | Absent | `100644` `0dfdc684a010ff2586fdf04cf67f4058ccdd9a51` |
| A | `tests/t1_simulation/calibration_fixtures.py` | Absent | `100644` `b9691f406ee416529c2ff33ec7d28100667404a8` |
| A | `tests/t1_simulation/test_calibration_gate.py` | Absent | `100644` `ccc9a2dc3b7712eef0d98a3c0ef58923869c69cb` |
| A | `tests/t1_simulation/test_calibration_native.py` | Absent | `100644` `363b871ad9e1a854af22c29889b58f41f2bdc4e6` |
| A | `tests/t1_simulation/test_calibration_outcomes.py` | Absent | `100644` `f235473896e71015b715cf85fac3a272bdfd91cc` |
| A | `tests/t1_simulation/test_calibration_verify_replay.py` | Absent | `100644` `9a1a7172f47ba8b74a58fba37cac9582480db9fb` |
| M | `tests/t1_simulation/test_command_integration.py` | `100644` `3170471d5be2ebbe02d72ac49ba2915e29698402` | `100644` `92b7483fcdeb4bbb0b6e6ed73d23dcb8ea342789` |
| M | `tests/t1_simulation/test_package.py` | `100644` `5162e34dade240a2a6d70ba88b47d81bcaeeab09` | `100644` `689a11daa7230e168d1dfde87638a6894af6ab00` |

## Build capture

The canonical build wire is `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/provider.wire`. It is **31,575 bytes**, with SHA-256 `f4f7c57ffdb673a709f1f36963515b71b7c335cb1575779a31351c76734895ef` and 32,768 filesystem-reported allocated bytes. The worker supervisor and the independent capped reader exited 0. Runtime finalization verified canonical `ct.build.v1` bytes, profile `bdw.checked-temperature.v1`, the exact checkpoint, clean application/backend source, the checked editions and all 198 source records, the interpreter and locked dependency evidence. It independently hashed the retained wire. Narrative readback matched that machine size, hash and checkpoint. The provider ran once.

The retained invocation and input ledger match their sealed bytes. The 138-byte command-line evidence matches the Bash argv `/bin/bash` `--` `/mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-21-c05-checkpoint-invocation-PID-SUCCESSOR/INVOCATION.sh.txt`. The submitted outer wrapper command is retained separately below.

## Preservation and ref classification

The baseline and final original-state records match on all six fields.

| Field | Before and after |
|---|---|
| Original symbolic HEAD | `refs/heads/codex/l2-installed-workflow` |
| Original object | `0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3` |
| Index SHA-256 | `2e28c61d9e09f664cc7f75b23fed89d4f9ad639642cfe023f6891c625f4943ad` |
| HEAD-file SHA-256 | `7c758e69d9d5ff367a99341725dab9546e4ac294f26d062a0f76f4aeca44db96` |
| Repository config SHA-256 | `00d98109f40591bd28899d25fb235df35be27235b4d5e8c8bcc646a9554a2204` |
| User config SHA-256 | `3bf56ec45032cbee58d95ccb9ca706b569e6a58faac7f0350f194c51015a7ec0` |

The stage-zero index had 2,710 entries under its sealed SHA-256. The raw packed-ref SHA-256 was `2ddf8f80fd63686648c38bb4c1ab0ca3f94dec41b9cbaf0c077be73f09be8f07` in the captured samples. The 30 original worktree registrations were preserved, with one exact new registration for the checkpoint.

| Ref difference | Name | Before | After |
|---|---|---|---|
| Disjoint removal relative to the authenticated historical census | `refs/codex/turn-diffs/checkpoints/5353191d0c339ef6bbf9514e3d29731a/3793f458e0d7ef13fa5a764d2b4ac563/1795139755936/45ab3ddf-dab6-43d8-b213-e71ab026ede3` | `ebce2f39647779f77644e3f938b14a5e921a49bb` | Absent |
| Disjoint addition relative to that census | `refs/codex/turn-diffs/checkpoints/5353191d0c339ef6bbf9514e3d29731a/90d37641e2652baba03262f6fe14cf07/1795228544002/403623d0-f9ad-4b19-bab2-369ee7797c08` | Absent | `d2ddf8f1b44e784797271438a03106946b0039aa` |
| Authorized target from runtime baseline through finalization | `refs/heads/codex/c05-companion-native-v2` | Absent | `f1e054cd4d5ed3e17c7c31e3532b16960e3c090c` via the exact parent |

The baseline classified the two historical changes as disjoint from protected inputs and target. No actor was inferred. Runtime went from 30 refs to 31 at branch creation, then advanced only the target. The paired stream comparison identified the target as the sole observed baseline-to-final ref difference. Whole-census equality was never an admission gate.

Both final inventories exited 0 and matched the finite pre-admission baselines. Historical coverage was 14,126 entries at SHA-256 `9735c7db24ca44fee0012923934aad61c1b7cd228331db203810fde3ed49c9b2`. Working coverage was 7,274 entries and 559,810,025 regular-file bytes at SHA-256 `16de5288493d551d90e5c5caeedf009bd604d526bf301893fd1de3b0b6ac187b`. These cover the 47 Appendix A scopes and specified reports, contracts, prior stops, component trees, diagnostic payload and named maintained paths, plus the separately selected untracked/diff-files working union. They are bounded filesystem comparisons.

The guarded session 70642 retains its exact 14 directories and five files totaling 3,219 bytes. Its journal still ends at OWNER-PAUSE-1 and its terminal records remain absent. Historical stopped attempts, issued authorities and freeze, C05 results and predecessor editions, the diagnostic payload, accepted temperature evidence and scoped R1/L1 acceptance retain their recorded dispositions. The 107 component passes remain attributed to attempts 03 and 04, with the checkpoint's 636 matching source records, parent-version runner and 14 exclusions recorded separately. D1 retains the accepted scoped interpretation, distinct policy identities and open wording limitation. L2/VM remain frozen and COOMET remains parked.

## Accounting and controller retention

| Sample | Measured value |
|---|---|
| Isolated worktree | 392,255,130 logical bytes, 400,297,984 allocated bytes, 2,995 entries. |
| Runtime evidence root | 106,956 logical bytes, 167,936 allocated bytes, 20 regular files. |
| Shared Git storage | 278,192,128 bytes before, 278,646,784 bytes after, 454,656 bytes growth. |
| Free space at bulk admission | 861,667,250,176 bytes on ext4, 978,223,026,176 on the repository volume. |
| Free space during finalization | 861,266,636,800 bytes on ext4, 978,222,567,424 on the repository volume. |

The samples satisfy the specified storage checks and are point observations. Historical allocation and host-wide transient usage remain unresolved. The machine terminal and capture records were present. The controller retained the merged stdout/stderr from every yield of the same execution session, including Git progress carriage returns and terminal output. No truncation or missing chunk was indicated. Receipt authoring began after the controller observed the outer exit. Its elapsed time and the later exclusive receipt readback are measured separately from runtime.

From `/mnt/d/operation-house-keeping`, the exact submitted command was

~~~~~sh
/usr/bin/env -i HOME=/home/mafasa PATH=/usr/bin:/bin LC_ALL=C.UTF-8 GIT_TERMINAL_PROMPT=0 /usr/bin/timeout --kill-after=3 1000 /bin/bash -- /mnt/d/operation-house-keeping/docs/superpowers/reports/2026-11-21-c05-checkpoint-invocation-PID-SUCCESSOR/INVOCATION.sh.txt </dev/null
~~~~~

Receipt authoring window before the exclusive write was 151.745 seconds, from outer exit observation 2026-11-21T06:21:19.927+00:00 to 2026-11-21T06:23:51.672+00:00. Final file storage, hash and the separate readback duration are measured after the write and returned with the receipt identity.

## Complete controller output

The merged stream is 42,968 UTF-8 bytes at SHA-256 `c48f22638412b008e93a53d4da4008939b2e30e6ef93087d6e32311ceaf830ac`.

~~~~~text
BASELINE_CLOCK=93372
2026-11-21T06:14:08,187836952+00:00
933.73 14714.56
CENSUS_BEGIN baseline
2026-11-21T06:14:08,191836945+00:00
933.73 14714.61
DISJOINT refs/codex/turn-diffs/checkpoints/5353191d0c339ef6bbf9514e3d29731a/3793f458e0d7ef13fa5a764d2b4ac563/1795139755936/45ab3ddf-dab6-43d8-b213-e71ab026ede3 ebce2f39647779f77644e3f938b14a5e921a49bb ABSENT direct protected inputs and target unaffected
DISJOINT refs/codex/turn-diffs/checkpoints/5353191d0c339ef6bbf9514e3d29731a/90d37641e2652baba03262f6fe14cf07/1795228544002/403623d0-f9ad-4b19-bab2-369ee7797c08 ABSENT d2ddf8f1b44e784797271438a03106946b0039aa direct protected inputs and target unaffected
2026-11-21T06:14:10,405197900+00:00
935.95 14748.94
CENSUS_EXIT baseline 0
BASELINE REFS
45fa23a5cae48de2f036d29a1f6b5095b320e733 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/0
ca49136b6e866e1b18341fcff8c265bb9d085e10 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/1
bbfcc706436ed94f69fad2cdd11911653b8864a3 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/2
d2ddf8f1b44e784797271438a03106946b0039aa refs/codex/turn-diffs/checkpoints/5353191d0c339ef6bbf9514e3d29731a/90d37641e2652baba03262f6fe14cf07/1795228544002/403623d0-f9ad-4b19-bab2-369ee7797c08
7bf6bb60d1e6178baf89b364b19ec6a8c7f539ce refs/codex/turn-diffs/checkpoints/85bdd771c1fc9b1f0e30283d59c5c68a/cba41569b7d881b5e8cc3ff7b7e0b330/1795127350819/4e197db1-52db-4f85-85ce-49a9ed96668b
532083cd75698f3efd20b128a6cbbf84d04ea7c8 refs/codex/turn-diffs/checkpoints/ef8d12e34e46d0dd299b3da04ecca7e4/7922686991a24a2d2dc8ed4dddcb3131/1795133149850/0e7613be-9dc0-449a-a5f9-c5906ebbbfd8
2bdebaf58bfccadd77ad553a93487033cad422d2 refs/heads/agents/ds-001-validation-complete
0ed77df7ea4870faec1eae9b89668add97aa855d refs/heads/bh001
d15debb1be89c6e25e9abe8de673d264bf6ef8ce refs/heads/brc-exp001
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/claude/t1-startup-chain-repair
c96faad2259fe98e9e878272ce459b137fcf9981 refs/heads/cn001
0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3 refs/heads/codex/l2-installed-workflow
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/codex/t1-startup-chain-repair
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/heads/codex/wip-pre-vm001-20260809
c2bc883d5309d489a920bb4bde8a3c4c129579ed refs/heads/ea001
7ffddca828ec361cea7fac0985ab99d5511bd76a refs/heads/es001
7693f1acf763f652947dff28b5dbb8a8dfee2505 refs/heads/fc001
5feadeb7b6cefe44c6da805eac0d329d361c7799 refs/heads/fl001
d888ba6fbfb313cf2f85ce5cb07168fb528ec059 refs/heads/fm001
0f7494c32d750c6e768f418559929100861d8de2 refs/heads/list
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/main
8a20dc82ef9445c311e89106ad10572c5c259df1 refs/heads/pt001
8cb5f1e1c0ae7b8d36bb0797188792cfc735b317 refs/heads/sn001
e44a18641ba6b440adcf9c10cd86d28376886942 refs/heads/st001
25b7cacb5aacc456d8d3507d5b76940772d94cda refs/heads/ta001
3842175dc4227ad5177c53ab437e70f857cceab4 refs/heads/vm001
46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6 refs/heads/vp001
1d6216f974531cb1c8fe7aeaaaf24b82b23b1e02 refs/heads/vs001
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/remotes/origin/codex/wip-pre-vm001-20260809
2f0afbd368105b99f0b8548ffece107918386e3d refs/remotes/origin/main
BASELINE WORKTREES
worktree /mnt/d/operation-house-keeping
HEAD 0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3
branch refs/heads/codex/l2-installed-workflow

worktree /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/nr-slice5-qualification-r1/checkouts/c321-real-process-v1
HEAD c321f2e096a71a43bf65787f6f1605c4031266e7
detached

worktree /tmp/ea001-sliceb-base-20260905
HEAD 70081b821569a82192f8e3fd100c2eec14beadb8
detached
prunable gitdir file points to non-existent location

worktree /tmp/ea001-sliceb-extras-20260905
HEAD 70081b821569a82192f8e3fd100c2eec14beadb8
detached
prunable gitdir file points to non-existent location

worktree /tmp/ea001-sliceb-repair-base-20260905
HEAD 932514a456bcafe690a94d2d774b61913c352fbf
detached
prunable gitdir file points to non-existent location

worktree /tmp/ea001-sliceb-repair-extras-20260905
HEAD 932514a456bcafe690a94d2d774b61913c352fbf
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-a-base-ECn1Oz/checkout
HEAD e49e7364c1ef14be6dbbf749f007baa9004363a5
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-a-extras-ImorPv/checkout
HEAD e49e7364c1ef14be6dbbf749f007baa9004363a5
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-a-final-base-DIdH07/checkout
HEAD 87473729a2d7cd9c62c2c5660a54f34de2e590e9
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-a-final-extras-5ZxAcO/checkout
HEAD 87473729a2d7cd9c62c2c5660a54f34de2e590e9
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-base-uJmgMH/checkout
HEAD 9737e9f137b80d526565e62e714f0603791dc3e6
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-extras-anPISJ/checkout
HEAD 9737e9f137b80d526565e62e714f0603791dc3e6
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-final2-base-SxFpyW/checkout
HEAD 5e717f5649b7091eb63f6f6ffafe07df3aaaa9f1
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-final2-extras-LQ2ysm/checkout
HEAD 5e717f5649b7091eb63f6f6ffafe07df3aaaa9f1
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-final3-base-SUMPAF/checkout
HEAD 9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-final3-extras-PWCiqO/checkout
HEAD 9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-base-clean-20260908
HEAD 6636af36d4cd4069afb2dda23a47057a66150a3a
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-base-clean-final
HEAD 6210d3c250b96f54b764a365cb0a3a988d9bf9f6
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-extras-clean-20260908
HEAD 6636af36d4cd4069afb2dda23a47057a66150a3a
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-extras-clean-final
HEAD 6210d3c250b96f54b764a365cb0a3a988d9bf9f6
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-slice-b-base-i14a9F
HEAD 4d8219d88d3f5f531c1a1cf250b36cb25e001c2f
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-slice-b-extras-SQT1fb
HEAD 4d8219d88d3f5f531c1a1cf250b36cb25e001c2f
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-final-release-clean
HEAD 23b60a42c2279fc228168967d47491b8983658fb
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-slice6-clean-5d4a42a
HEAD 5d4a42a6ab8979be5077eed0c6f00cadef2c79dc
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-slice6-clean-f18491d
HEAD c06395859019bead8cb7cc6491fde3efd04f1524
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-slice6-disposition-clean
HEAD 96f71b7f987faacaf7f16c361018434e4ae21993
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-slice6-final-clean
HEAD 276c8bf0d3126daba2a89ef6689b4c0de43517d5
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-slice6-oracle-clean
HEAD 01dde502af7eacd5b0daed547bae1954ad922e70
detached
prunable gitdir file points to non-existent location

worktree /tmp/ta001-slice-b-base-clean-20260907
HEAD 2ec18f7234273dba98098d268df4568d5cc84d85
detached
prunable gitdir file points to non-existent location

worktree /tmp/ta001-slice-b-extras-clean-20260907
HEAD 2ec18f7234273dba98098d268df4568d5cc84d85
detached
prunable gitdir file points to non-existent location
BASELINE ORIGINAL
2e28c61d9e09f664cc7f75b23fed89d4f9ad639642cfe023f6891c625f4943ad  .git/index
7c758e69d9d5ff367a99341725dab9546e4ac294f26d062a0f76f4aeca44db96  .git/HEAD
00d98109f40591bd28899d25fb235df35be27235b4d5e8c8bcc646a9554a2204  .git/config
3bf56ec45032cbee58d95ccb9ca706b569e6a58faac7f0350f194c51015a7ec0  /home/mafasa/.gitconfig
refs/heads/codex/l2-installed-workflow
0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3
2ddf8f80fd63686648c38bb4c1ab0ca3f94dec41b9cbaf0c077be73f09be8f07  .git/packed-refs
baseline 17 postimages; 636 component matches; 198 provider inputs; 2315373 bytes; two contract pins
HIST_BEFORE=14126 9735c7db24ca44fee0012923934aad61c1b7cd228331db203810fde3ed49c9b2
WORK_BEFORE=7274 entries 559810025 bytes 16de5288493d551d90e5c5caeedf009bd604d526bf301893fd1de3b0b6ac187b
MEMBERSHIP_BEFORE=ae1a75fec30866ec841b1a3294fcf13d350e1ddf9c83b238a2f8b061c90e410a  -
ADMISSION_CLOCK=107172
2026-11-21T06:16:20,018794521+00:00
1071.73 16859.16
CENSUS_BEGIN bulk
2026-11-21T06:16:20,022750595+00:00
1071.73 16859.20
2026-11-21T06:16:22,328828806+00:00
1074.04 16895.03
CENSUS_EXIT bulk 0
BULK REFS
45fa23a5cae48de2f036d29a1f6b5095b320e733 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/0
ca49136b6e866e1b18341fcff8c265bb9d085e10 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/1
bbfcc706436ed94f69fad2cdd11911653b8864a3 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/2
d2ddf8f1b44e784797271438a03106946b0039aa refs/codex/turn-diffs/checkpoints/5353191d0c339ef6bbf9514e3d29731a/90d37641e2652baba03262f6fe14cf07/1795228544002/403623d0-f9ad-4b19-bab2-369ee7797c08
7bf6bb60d1e6178baf89b364b19ec6a8c7f539ce refs/codex/turn-diffs/checkpoints/85bdd771c1fc9b1f0e30283d59c5c68a/cba41569b7d881b5e8cc3ff7b7e0b330/1795127350819/4e197db1-52db-4f85-85ce-49a9ed96668b
532083cd75698f3efd20b128a6cbbf84d04ea7c8 refs/codex/turn-diffs/checkpoints/ef8d12e34e46d0dd299b3da04ecca7e4/7922686991a24a2d2dc8ed4dddcb3131/1795133149850/0e7613be-9dc0-449a-a5f9-c5906ebbbfd8
2bdebaf58bfccadd77ad553a93487033cad422d2 refs/heads/agents/ds-001-validation-complete
0ed77df7ea4870faec1eae9b89668add97aa855d refs/heads/bh001
d15debb1be89c6e25e9abe8de673d264bf6ef8ce refs/heads/brc-exp001
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/claude/t1-startup-chain-repair
c96faad2259fe98e9e878272ce459b137fcf9981 refs/heads/cn001
0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3 refs/heads/codex/l2-installed-workflow
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/codex/t1-startup-chain-repair
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/heads/codex/wip-pre-vm001-20260809
c2bc883d5309d489a920bb4bde8a3c4c129579ed refs/heads/ea001
7ffddca828ec361cea7fac0985ab99d5511bd76a refs/heads/es001
7693f1acf763f652947dff28b5dbb8a8dfee2505 refs/heads/fc001
5feadeb7b6cefe44c6da805eac0d329d361c7799 refs/heads/fl001
d888ba6fbfb313cf2f85ce5cb07168fb528ec059 refs/heads/fm001
0f7494c32d750c6e768f418559929100861d8de2 refs/heads/list
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/main
8a20dc82ef9445c311e89106ad10572c5c259df1 refs/heads/pt001
8cb5f1e1c0ae7b8d36bb0797188792cfc735b317 refs/heads/sn001
e44a18641ba6b440adcf9c10cd86d28376886942 refs/heads/st001
25b7cacb5aacc456d8d3507d5b76940772d94cda refs/heads/ta001
3842175dc4227ad5177c53ab437e70f857cceab4 refs/heads/vm001
46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6 refs/heads/vp001
1d6216f974531cb1c8fe7aeaaaf24b82b23b1e02 refs/heads/vs001
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/remotes/origin/codex/wip-pre-vm001-20260809
2f0afbd368105b99f0b8548ffece107918386e3d refs/remotes/origin/main
2ddf8f80fd63686648c38bb4c1ab0ca3f94dec41b9cbaf0c077be73f09be8f07  .git/packed-refs
Filesystem         1B-blocks         Used    Available Use% Mounted on
/dev/sdc       1081101176832 164441571328 861667250176  17% /
D:\            1000202235904  21979209728 978223026176   3% /mnt/d
GIT_BEFORE=278192128
bulk 17 postimages; 636 component matches; 198 provider inputs; 2315373 bytes; two contract pins
2620 parent objects bulk
IMMEDIATE_CLOCK=120948
2026-11-21T06:18:31,511514186+00:00
1209.48 18998.19
2620 parent objects immediate
immediate 17 postimages; 636 component matches; 198 provider inputs; 2315373 bytes; two contract pins
CENSUS_BEGIN immediate
2026-11-21T06:18:50,087727167+00:00
1229.60 19309.93
2026-11-21T06:18:52,304800051+00:00
1231.82 19344.33
CENSUS_EXIT immediate 0
IMMEDIATE REFS
45fa23a5cae48de2f036d29a1f6b5095b320e733 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/0
ca49136b6e866e1b18341fcff8c265bb9d085e10 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/1
bbfcc706436ed94f69fad2cdd11911653b8864a3 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/2
d2ddf8f1b44e784797271438a03106946b0039aa refs/codex/turn-diffs/checkpoints/5353191d0c339ef6bbf9514e3d29731a/90d37641e2652baba03262f6fe14cf07/1795228544002/403623d0-f9ad-4b19-bab2-369ee7797c08
7bf6bb60d1e6178baf89b364b19ec6a8c7f539ce refs/codex/turn-diffs/checkpoints/85bdd771c1fc9b1f0e30283d59c5c68a/cba41569b7d881b5e8cc3ff7b7e0b330/1795127350819/4e197db1-52db-4f85-85ce-49a9ed96668b
532083cd75698f3efd20b128a6cbbf84d04ea7c8 refs/codex/turn-diffs/checkpoints/ef8d12e34e46d0dd299b3da04ecca7e4/7922686991a24a2d2dc8ed4dddcb3131/1795133149850/0e7613be-9dc0-449a-a5f9-c5906ebbbfd8
2bdebaf58bfccadd77ad553a93487033cad422d2 refs/heads/agents/ds-001-validation-complete
0ed77df7ea4870faec1eae9b89668add97aa855d refs/heads/bh001
d15debb1be89c6e25e9abe8de673d264bf6ef8ce refs/heads/brc-exp001
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/claude/t1-startup-chain-repair
c96faad2259fe98e9e878272ce459b137fcf9981 refs/heads/cn001
0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3 refs/heads/codex/l2-installed-workflow
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/codex/t1-startup-chain-repair
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/heads/codex/wip-pre-vm001-20260809
c2bc883d5309d489a920bb4bde8a3c4c129579ed refs/heads/ea001
7ffddca828ec361cea7fac0985ab99d5511bd76a refs/heads/es001
7693f1acf763f652947dff28b5dbb8a8dfee2505 refs/heads/fc001
5feadeb7b6cefe44c6da805eac0d329d361c7799 refs/heads/fl001
d888ba6fbfb313cf2f85ce5cb07168fb528ec059 refs/heads/fm001
0f7494c32d750c6e768f418559929100861d8de2 refs/heads/list
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/main
8a20dc82ef9445c311e89106ad10572c5c259df1 refs/heads/pt001
8cb5f1e1c0ae7b8d36bb0797188792cfc735b317 refs/heads/sn001
e44a18641ba6b440adcf9c10cd86d28376886942 refs/heads/st001
25b7cacb5aacc456d8d3507d5b76940772d94cda refs/heads/ta001
3842175dc4227ad5177c53ab437e70f857cceab4 refs/heads/vm001
46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6 refs/heads/vp001
1d6216f974531cb1c8fe7aeaaaf24b82b23b1e02 refs/heads/vs001
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/remotes/origin/codex/wip-pre-vm001-20260809
2f0afbd368105b99f0b8548ffece107918386e3d refs/remotes/origin/main
CENSUS_BEGIN fast
2026-11-21T06:18:52,400195703+00:00
1231.91 19345.78
2026-11-21T06:18:54,760089857+00:00
1234.27 19382.40
CENSUS_EXIT fast 0
FAST REFS
45fa23a5cae48de2f036d29a1f6b5095b320e733 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/0
ca49136b6e866e1b18341fcff8c265bb9d085e10 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/1
bbfcc706436ed94f69fad2cdd11911653b8864a3 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/2
d2ddf8f1b44e784797271438a03106946b0039aa refs/codex/turn-diffs/checkpoints/5353191d0c339ef6bbf9514e3d29731a/90d37641e2652baba03262f6fe14cf07/1795228544002/403623d0-f9ad-4b19-bab2-369ee7797c08
7bf6bb60d1e6178baf89b364b19ec6a8c7f539ce refs/codex/turn-diffs/checkpoints/85bdd771c1fc9b1f0e30283d59c5c68a/cba41569b7d881b5e8cc3ff7b7e0b330/1795127350819/4e197db1-52db-4f85-85ce-49a9ed96668b
532083cd75698f3efd20b128a6cbbf84d04ea7c8 refs/codex/turn-diffs/checkpoints/ef8d12e34e46d0dd299b3da04ecca7e4/7922686991a24a2d2dc8ed4dddcb3131/1795133149850/0e7613be-9dc0-449a-a5f9-c5906ebbbfd8
2bdebaf58bfccadd77ad553a93487033cad422d2 refs/heads/agents/ds-001-validation-complete
0ed77df7ea4870faec1eae9b89668add97aa855d refs/heads/bh001
d15debb1be89c6e25e9abe8de673d264bf6ef8ce refs/heads/brc-exp001
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/claude/t1-startup-chain-repair
c96faad2259fe98e9e878272ce459b137fcf9981 refs/heads/cn001
0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3 refs/heads/codex/l2-installed-workflow
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/codex/t1-startup-chain-repair
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/heads/codex/wip-pre-vm001-20260809
c2bc883d5309d489a920bb4bde8a3c4c129579ed refs/heads/ea001
7ffddca828ec361cea7fac0985ab99d5511bd76a refs/heads/es001
7693f1acf763f652947dff28b5dbb8a8dfee2505 refs/heads/fc001
5feadeb7b6cefe44c6da805eac0d329d361c7799 refs/heads/fl001
d888ba6fbfb313cf2f85ce5cb07168fb528ec059 refs/heads/fm001
0f7494c32d750c6e768f418559929100861d8de2 refs/heads/list
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/main
8a20dc82ef9445c311e89106ad10572c5c259df1 refs/heads/pt001
8cb5f1e1c0ae7b8d36bb0797188792cfc735b317 refs/heads/sn001
e44a18641ba6b440adcf9c10cd86d28376886942 refs/heads/st001
25b7cacb5aacc456d8d3507d5b76940772d94cda refs/heads/ta001
3842175dc4227ad5177c53ab437e70f857cceab4 refs/heads/vm001
46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6 refs/heads/vp001
1d6216f974531cb1c8fe7aeaaaf24b82b23b1e02 refs/heads/vs001
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/remotes/origin/codex/wip-pre-vm001-20260809
2f0afbd368105b99f0b8548ffece107918386e3d refs/remotes/origin/main
CHECKPOINT_CLOCK=123427
2026-11-21T06:18:54,768364934+00:00
1234.28 19382.52
2a61ed1849c3861380da735ab552dabe9f5c52e6319de9fad378c034ee003a85  /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/baseline.refs
2fbd4d3fbe7ed4a53f42d820020e99831fc42d5ec40dd7fec9221868e8c0ca5f  /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/baseline.worktrees
bridge 17 postimages; 636 component matches; 198 provider inputs; 2315373 bytes; two contract pins
2620 parent objects bridge
CENSUS_BEGIN pre-git
2026-11-21T06:19:08,882180905+00:00
1248.39 19602.02
2026-11-21T06:19:09,717306424+00:00
1250.92 19641.35
CENSUS_EXIT pre-git 0
PREGIT REFS
45fa23a5cae48de2f036d29a1f6b5095b320e733 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/0
ca49136b6e866e1b18341fcff8c265bb9d085e10 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/1
bbfcc706436ed94f69fad2cdd11911653b8864a3 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/2
d2ddf8f1b44e784797271438a03106946b0039aa refs/codex/turn-diffs/checkpoints/5353191d0c339ef6bbf9514e3d29731a/90d37641e2652baba03262f6fe14cf07/1795228544002/403623d0-f9ad-4b19-bab2-369ee7797c08
7bf6bb60d1e6178baf89b364b19ec6a8c7f539ce refs/codex/turn-diffs/checkpoints/85bdd771c1fc9b1f0e30283d59c5c68a/cba41569b7d881b5e8cc3ff7b7e0b330/1795127350819/4e197db1-52db-4f85-85ce-49a9ed96668b
532083cd75698f3efd20b128a6cbbf84d04ea7c8 refs/codex/turn-diffs/checkpoints/ef8d12e34e46d0dd299b3da04ecca7e4/7922686991a24a2d2dc8ed4dddcb3131/1795133149850/0e7613be-9dc0-449a-a5f9-c5906ebbbfd8
2bdebaf58bfccadd77ad553a93487033cad422d2 refs/heads/agents/ds-001-validation-complete
0ed77df7ea4870faec1eae9b89668add97aa855d refs/heads/bh001
d15debb1be89c6e25e9abe8de673d264bf6ef8ce refs/heads/brc-exp001
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/claude/t1-startup-chain-repair
c96faad2259fe98e9e878272ce459b137fcf9981 refs/heads/cn001
0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3 refs/heads/codex/l2-installed-workflow
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/codex/t1-startup-chain-repair
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/heads/codex/wip-pre-vm001-20260809
c2bc883d5309d489a920bb4bde8a3c4c129579ed refs/heads/ea001
7ffddca828ec361cea7fac0985ab99d5511bd76a refs/heads/es001
7693f1acf763f652947dff28b5dbb8a8dfee2505 refs/heads/fc001
5feadeb7b6cefe44c6da805eac0d329d361c7799 refs/heads/fl001
d888ba6fbfb313cf2f85ce5cb07168fb528ec059 refs/heads/fm001
0f7494c32d750c6e768f418559929100861d8de2 refs/heads/list
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/main
8a20dc82ef9445c311e89106ad10572c5c259df1 refs/heads/pt001
8cb5f1e1c0ae7b8d36bb0797188792cfc735b317 refs/heads/sn001
e44a18641ba6b440adcf9c10cd86d28376886942 refs/heads/st001
25b7cacb5aacc456d8d3507d5b76940772d94cda refs/heads/ta001
3842175dc4227ad5177c53ab437e70f857cceab4 refs/heads/vm001
46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6 refs/heads/vp001
1d6216f974531cb1c8fe7aeaaaf24b82b23b1e02 refs/heads/vs001
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/remotes/origin/codex/wip-pre-vm001-20260809
2f0afbd368105b99f0b8548ffece107918386e3d refs/remotes/origin/main
WORKTREE_ADD_DISPATCH
Preparing worktree (new branch 'codex/c05-companion-native-v2')
Updating files:  11% (303/2710)Updating files:  12% (326/2710)Updating files:  13% (353/2710)Updating files:  14% (380/2710)Updating files:  15% (407/2710)Updating files:  16% (434/2710)Updating files:  17% (461/2710)Updating files:  17% (472/2710)Updating files:  18% (488/2710)Updating files:  19% (515/2710)Updating files:  19% (525/2710)Updating files:  20% (542/2710)Updating files:  21% (570/2710)Updating files:  21% (583/2710)Updating files:  22% (597/2710)Updating files:  23% (624/2710)Updating files:  24% (651/2710)Updating files:  25% (678/2710)Updating files:  26% (705/2710)Updating files:  26% (707/2710)Updating files:  27% (732/2710)Updating files:  28% (759/2710)Updating files:  29% (786/2710)Updating files:  30% (813/2710)Updating files:  31% (841/2710)Updating files:  32% (868/2710)Updating files:  33% (895/2710)Updating files:  34% (922/2710)Updating files:  35% (949/2710)Updating files:  35% (952/2710)Updating files:  36% (976/2710)Updating files:  37% (1003/2710)Updating files:  38% (1030/2710)Updating files:  39% (1057/2710)Updating files:  40% (1084/2710)Updating files:  41% (1112/2710)Updating files:  42% (1139/2710)Updating files:  43% (1166/2710)Updating files:  43% (1175/2710)Updating files:  44% (1193/2710)Updating files:  45% (1220/2710)Updating files:  46% (1247/2710)Updating files:  47% (1274/2710)Updating files:  48% (1301/2710)Updating files:  49% (1328/2710)Updating files:  49% (1344/2710)Updating files:  50% (1355/2710)Updating files:  51% (1383/2710)Updating files:  52% (1410/2710)Updating files:  53% (1437/2710)Updating files:  54% (1464/2710)Updating files:  55% (1491/2710)Updating files:  56% (1518/2710)Updating files:  57% (1545/2710)Updating files:  57% (1567/2710)Updating files:  58% (1572/2710)Updating files:  59% (1599/2710)Updating files:  60% (1626/2710)Updating files:  61% (1654/2710)Updating files:  62% (1681/2710)Updating files:  63% (1708/2710)Updating files:  64% (1735/2710)Updating files:  65% (1762/2710)Updating files:  66% (1789/2710)Updating files:  66% (1796/2710)Updating files:  67% (1816/2710)Updating files:  68% (1843/2710)Updating files:  69% (1870/2710)Updating files:  70% (1897/2710)Updating files:  71% (1925/2710)Updating files:  71% (1941/2710)Updating files:  71% (1949/2710)Updating files:  72% (1952/2710)Updating files:  73% (1979/2710)Updating files:  74% (2006/2710)Updating files:  74% (2013/2710)Updating files:  75% (2033/2710)Updating files:  75% (2051/2710)Updating files:  76% (2060/2710)Updating files:  76% (2083/2710)Updating files:  77% (2087/2710)Updating files:  78% (2114/2710)Updating files:  79% (2141/2710)Updating files:  79% (2152/2710)Updating files:  79% (2167/2710)Updating files:  80% (2168/2710)Updating files:  81% (2196/2710)Updating files:  82% (2223/2710)Updating files:  83% (2250/2710)Updating files:  84% (2277/2710)Updating files:  85% (2304/2710)Updating files:  86% (2331/2710)Updating files:  87% (2358/2710)Updating files:  88% (2385/2710)Updating files:  89% (2412/2710)Updating files:  90% (2439/2710)Updating files:  91% (2467/2710)Updating files:  92% (2494/2710)Updating files:  93% (2521/2710)Updating files:  94% (2548/2710)Updating files:  95% (2575/2710)Updating files:  95% (2599/2710)Updating files:  96% (2602/2710)Updating files:  97% (2629/2710)Updating files:  98% (2656/2710)Updating files:  99% (2683/2710)Updating files: 100% (2710/2710)Updating files: 100% (2710/2710), done.
HEAD is now at 0a39c4d Add L1/L2 installed-release portability, rebinding tool and validation records
WORKTREE_ADD_EXIT=0
BRANCH AT PARENT REFS
45fa23a5cae48de2f036d29a1f6b5095b320e733 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/0
ca49136b6e866e1b18341fcff8c265bb9d085e10 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/1
bbfcc706436ed94f69fad2cdd11911653b8864a3 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/2
d2ddf8f1b44e784797271438a03106946b0039aa refs/codex/turn-diffs/checkpoints/5353191d0c339ef6bbf9514e3d29731a/90d37641e2652baba03262f6fe14cf07/1795228544002/403623d0-f9ad-4b19-bab2-369ee7797c08
7bf6bb60d1e6178baf89b364b19ec6a8c7f539ce refs/codex/turn-diffs/checkpoints/85bdd771c1fc9b1f0e30283d59c5c68a/cba41569b7d881b5e8cc3ff7b7e0b330/1795127350819/4e197db1-52db-4f85-85ce-49a9ed96668b
532083cd75698f3efd20b128a6cbbf84d04ea7c8 refs/codex/turn-diffs/checkpoints/ef8d12e34e46d0dd299b3da04ecca7e4/7922686991a24a2d2dc8ed4dddcb3131/1795133149850/0e7613be-9dc0-449a-a5f9-c5906ebbbfd8
2bdebaf58bfccadd77ad553a93487033cad422d2 refs/heads/agents/ds-001-validation-complete
0ed77df7ea4870faec1eae9b89668add97aa855d refs/heads/bh001
d15debb1be89c6e25e9abe8de673d264bf6ef8ce refs/heads/brc-exp001
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/claude/t1-startup-chain-repair
c96faad2259fe98e9e878272ce459b137fcf9981 refs/heads/cn001
0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3 refs/heads/codex/c05-companion-native-v2
0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3 refs/heads/codex/l2-installed-workflow
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/codex/t1-startup-chain-repair
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/heads/codex/wip-pre-vm001-20260809
c2bc883d5309d489a920bb4bde8a3c4c129579ed refs/heads/ea001
7ffddca828ec361cea7fac0985ab99d5511bd76a refs/heads/es001
7693f1acf763f652947dff28b5dbb8a8dfee2505 refs/heads/fc001
5feadeb7b6cefe44c6da805eac0d329d361c7799 refs/heads/fl001
d888ba6fbfb313cf2f85ce5cb07168fb528ec059 refs/heads/fm001
0f7494c32d750c6e768f418559929100861d8de2 refs/heads/list
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/main
8a20dc82ef9445c311e89106ad10572c5c259df1 refs/heads/pt001
8cb5f1e1c0ae7b8d36bb0797188792cfc735b317 refs/heads/sn001
e44a18641ba6b440adcf9c10cd86d28376886942 refs/heads/st001
25b7cacb5aacc456d8d3507d5b76940772d94cda refs/heads/ta001
3842175dc4227ad5177c53ab437e70f857cceab4 refs/heads/vm001
46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6 refs/heads/vp001
1d6216f974531cb1c8fe7aeaaaf24b82b23b1e02 refs/heads/vs001
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/remotes/origin/codex/wip-pre-vm001-20260809
2f0afbd368105b99f0b8548ffece107918386e3d refs/remotes/origin/main
STAGE_DISPATCH
staged 17 postimages; 636 component matches; 198 provider inputs; 2315373 bytes; two contract pins
2026-11-21T06:19:45,823825598+00:00
1288.59 20226.22
COMMIT_DISPATCH
[codex/c05-companion-native-v2 f1e054c] Checkpoint the scoped C05 companion calibration gate
 17 files changed, 5757 insertions(+), 58 deletions(-)
 create mode 100644 applications/bounded_decision_workflow/t1_calibration_gate.py
 create mode 100644 applications/bounded_decision_workflow/t1_calibration_schemas.json
 create mode 100644 applications/bounded_decision_workflow/t1_calibration_schemas_v2.json
 create mode 100644 docs/superpowers/specs/2026-11-19-c05-companion-gate-v1/CONTRACT.md
 create mode 100644 docs/superpowers/specs/2026-11-20-c05-companion-gate-v2/CONTRACT.md
 create mode 100644 tests/t1_simulation/calibration_fixtures.py
 create mode 100644 tests/t1_simulation/test_calibration_gate.py
 create mode 100644 tests/t1_simulation/test_calibration_native.py
 create mode 100644 tests/t1_simulation/test_calibration_outcomes.py
 create mode 100644 tests/t1_simulation/test_calibration_verify_replay.py
COMMIT_EXIT=0 NEW_COMMIT=f1e054cd4d5ed3e17c7c31e3532b16960e3c090c
commit 17 postimages; 636 component matches; 198 provider inputs; 2315373 bytes; two contract pins
commit f1e054cd4d5ed3e17c7c31e3532b16960e3c090c
Author:     MafasaBytes <masiakwalakl@outlook.com>
AuthorDate: Sat Nov 21 07:19:46 2026 +0100
Commit:     MafasaBytes <masiakwalakl@outlook.com>
CommitDate: Sat Nov 21 07:19:46 2026 +0100

    Checkpoint the scoped C05 companion calibration gate
    
    Retain the producer-checked pre-delegation gate, both companion editions and their focused tests. Preserve distinct source and assessment policy bindings.
    
    The C05 component checkpoint comprises 92 recorded passes in attempt 03 and 15 in attempt 04. Native build capture and scientific validation are separate.
M	applications/bounded_decision_workflow/checked_runtime.py
A	applications/bounded_decision_workflow/t1_calibration_gate.py
A	applications/bounded_decision_workflow/t1_calibration_schemas.json
A	applications/bounded_decision_workflow/t1_calibration_schemas_v2.json
M	applications/bounded_decision_workflow/t1_cli.py
M	applications/bounded_decision_workflow/t1_package.py
M	applications/bounded_decision_workflow/t1_schemas.py
M	applications/bounded_decision_workflow/t1_workflow.py
A	docs/superpowers/specs/2026-11-19-c05-companion-gate-v1/CONTRACT.md
A	docs/superpowers/specs/2026-11-20-c05-companion-gate-v2/CONTRACT.md
A	tests/t1_simulation/calibration_fixtures.py
A	tests/t1_simulation/test_calibration_gate.py
A	tests/t1_simulation/test_calibration_native.py
A	tests/t1_simulation/test_calibration_outcomes.py
A	tests/t1_simulation/test_calibration_verify_replay.py
M	tests/t1_simulation/test_command_integration.py
M	tests/t1_simulation/test_package.py
a738cf4536726aff95b154baf0a41742e77012a4
STORAGE 392255130 400297984 2995 278192128 278646784
2026-11-21T06:20:06,991052405+00:00
1309.75 20555.28
WORKER_SUPERVISOR_RC=0 READER_RC=0
2026-11-21T06:20:08,634835650+00:00
1311.40 20579.92
OPERATION_TERMINAL phase=capture rc=0 final_start=131140
2026-11-21T06:20:08,642690147+00:00
1311.40 20580.02
CAPTURE_TERMINAL worker_supervisor=0 reader=0
BUILD 31575 f4f7c57ffdb673a709f1f36963515b71b7c335cb1575779a31351c76734895ef
f4f7c57ffdb673a709f1f36963515b71b7c335cb1575779a31351c76734895ef  /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/provider.wire
AFTER ORIGINAL
2e28c61d9e09f664cc7f75b23fed89d4f9ad639642cfe023f6891c625f4943ad  .git/index
7c758e69d9d5ff367a99341725dab9546e4ac294f26d062a0f76f4aeca44db96  .git/HEAD
00d98109f40591bd28899d25fb235df35be27235b4d5e8c8bcc646a9554a2204  .git/config
3bf56ec45032cbee58d95ccb9ca706b569e6a58faac7f0350f194c51015a7ec0  /home/mafasa/.gitconfig
refs/heads/codex/l2-installed-workflow
0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3
AFTER WORKTREES
worktree /mnt/d/operation-house-keeping
HEAD 0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3
branch refs/heads/codex/l2-installed-workflow

worktree /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-src-20261120-01
HEAD f1e054cd4d5ed3e17c7c31e3532b16960e3c090c
branch refs/heads/codex/c05-companion-native-v2

worktree /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/nr-slice5-qualification-r1/checkouts/c321-real-process-v1
HEAD c321f2e096a71a43bf65787f6f1605c4031266e7
detached

worktree /tmp/ea001-sliceb-base-20260905
HEAD 70081b821569a82192f8e3fd100c2eec14beadb8
detached
prunable gitdir file points to non-existent location

worktree /tmp/ea001-sliceb-extras-20260905
HEAD 70081b821569a82192f8e3fd100c2eec14beadb8
detached
prunable gitdir file points to non-existent location

worktree /tmp/ea001-sliceb-repair-base-20260905
HEAD 932514a456bcafe690a94d2d774b61913c352fbf
detached
prunable gitdir file points to non-existent location

worktree /tmp/ea001-sliceb-repair-extras-20260905
HEAD 932514a456bcafe690a94d2d774b61913c352fbf
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-a-base-ECn1Oz/checkout
HEAD e49e7364c1ef14be6dbbf749f007baa9004363a5
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-a-extras-ImorPv/checkout
HEAD e49e7364c1ef14be6dbbf749f007baa9004363a5
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-a-final-base-DIdH07/checkout
HEAD 87473729a2d7cd9c62c2c5660a54f34de2e590e9
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-a-final-extras-5ZxAcO/checkout
HEAD 87473729a2d7cd9c62c2c5660a54f34de2e590e9
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-base-uJmgMH/checkout
HEAD 9737e9f137b80d526565e62e714f0603791dc3e6
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-extras-anPISJ/checkout
HEAD 9737e9f137b80d526565e62e714f0603791dc3e6
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-final2-base-SxFpyW/checkout
HEAD 5e717f5649b7091eb63f6f6ffafe07df3aaaa9f1
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-final2-extras-LQ2ysm/checkout
HEAD 5e717f5649b7091eb63f6f6ffafe07df3aaaa9f1
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-final3-base-SUMPAF/checkout
HEAD 9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082
detached
prunable gitdir file points to non-existent location

worktree /tmp/fc001-slice-b-final3-extras-PWCiqO/checkout
HEAD 9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-base-clean-20260908
HEAD 6636af36d4cd4069afb2dda23a47057a66150a3a
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-base-clean-final
HEAD 6210d3c250b96f54b764a365cb0a3a988d9bf9f6
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-extras-clean-20260908
HEAD 6636af36d4cd4069afb2dda23a47057a66150a3a
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-extras-clean-final
HEAD 6210d3c250b96f54b764a365cb0a3a988d9bf9f6
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-slice-b-base-i14a9F
HEAD 4d8219d88d3f5f531c1a1cf250b36cb25e001c2f
detached
prunable gitdir file points to non-existent location

worktree /tmp/fm001-slice-b-extras-SQT1fb
HEAD 4d8219d88d3f5f531c1a1cf250b36cb25e001c2f
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-final-release-clean
HEAD 23b60a42c2279fc228168967d47491b8983658fb
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-slice6-clean-5d4a42a
HEAD 5d4a42a6ab8979be5077eed0c6f00cadef2c79dc
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-slice6-clean-f18491d
HEAD c06395859019bead8cb7cc6491fde3efd04f1524
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-slice6-disposition-clean
HEAD 96f71b7f987faacaf7f16c361018434e4ae21993
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-slice6-final-clean
HEAD 276c8bf0d3126daba2a89ef6689b4c0de43517d5
detached
prunable gitdir file points to non-existent location

worktree /tmp/nm-slice6-oracle-clean
HEAD 01dde502af7eacd5b0daed547bae1954ad922e70
detached
prunable gitdir file points to non-existent location

worktree /tmp/ta001-slice-b-base-clean-20260907
HEAD 2ec18f7234273dba98098d268df4568d5cc84d85
detached
prunable gitdir file points to non-existent location

worktree /tmp/ta001-slice-b-extras-clean-20260907
HEAD 2ec18f7234273dba98098d268df4568d5cc84d85
detached
prunable gitdir file points to non-existent location
AFTER REFS
45fa23a5cae48de2f036d29a1f6b5095b320e733 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/0
ca49136b6e866e1b18341fcff8c265bb9d085e10 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/1
bbfcc706436ed94f69fad2cdd11911653b8864a3 refs/agents/1b7c9f80-e775-4ed4-99e9-b4e45fb61cbf/checkpoints/turn/2
d2ddf8f1b44e784797271438a03106946b0039aa refs/codex/turn-diffs/checkpoints/5353191d0c339ef6bbf9514e3d29731a/90d37641e2652baba03262f6fe14cf07/1795228544002/403623d0-f9ad-4b19-bab2-369ee7797c08
7bf6bb60d1e6178baf89b364b19ec6a8c7f539ce refs/codex/turn-diffs/checkpoints/85bdd771c1fc9b1f0e30283d59c5c68a/cba41569b7d881b5e8cc3ff7b7e0b330/1795127350819/4e197db1-52db-4f85-85ce-49a9ed96668b
532083cd75698f3efd20b128a6cbbf84d04ea7c8 refs/codex/turn-diffs/checkpoints/ef8d12e34e46d0dd299b3da04ecca7e4/7922686991a24a2d2dc8ed4dddcb3131/1795133149850/0e7613be-9dc0-449a-a5f9-c5906ebbbfd8
2bdebaf58bfccadd77ad553a93487033cad422d2 refs/heads/agents/ds-001-validation-complete
0ed77df7ea4870faec1eae9b89668add97aa855d refs/heads/bh001
d15debb1be89c6e25e9abe8de673d264bf6ef8ce refs/heads/brc-exp001
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/claude/t1-startup-chain-repair
c96faad2259fe98e9e878272ce459b137fcf9981 refs/heads/cn001
f1e054cd4d5ed3e17c7c31e3532b16960e3c090c refs/heads/codex/c05-companion-native-v2
0a39c4d8f86c3e996aa97adc9d0afb2eed4faca3 refs/heads/codex/l2-installed-workflow
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/codex/t1-startup-chain-repair
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/heads/codex/wip-pre-vm001-20260809
c2bc883d5309d489a920bb4bde8a3c4c129579ed refs/heads/ea001
7ffddca828ec361cea7fac0985ab99d5511bd76a refs/heads/es001
7693f1acf763f652947dff28b5dbb8a8dfee2505 refs/heads/fc001
5feadeb7b6cefe44c6da805eac0d329d361c7799 refs/heads/fl001
d888ba6fbfb313cf2f85ce5cb07168fb528ec059 refs/heads/fm001
0f7494c32d750c6e768f418559929100861d8de2 refs/heads/list
07055c6357a049dba4599b527a1ce261ec529a2c refs/heads/main
8a20dc82ef9445c311e89106ad10572c5c259df1 refs/heads/pt001
8cb5f1e1c0ae7b8d36bb0797188792cfc735b317 refs/heads/sn001
e44a18641ba6b440adcf9c10cd86d28376886942 refs/heads/st001
25b7cacb5aacc456d8d3507d5b76940772d94cda refs/heads/ta001
3842175dc4227ad5177c53ab437e70f857cceab4 refs/heads/vm001
46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6 refs/heads/vp001
1d6216f974531cb1c8fe7aeaaaf24b82b23b1e02 refs/heads/vs001
7b15cb1912bb58500fc6208c7489876ed74cdfc0 refs/remotes/origin/codex/wip-pre-vm001-20260809
2f0afbd368105b99f0b8548ffece107918386e3d refs/remotes/origin/main
2ddf8f80fd63686648c38bb4c1ab0ca3f94dec41b9cbaf0c077be73f09be8f07  .git/packed-refs
AUTHORIZED target advance refs/heads/codex/c05-companion-native-v2 f1e054cd4d5ed3e17c7c31e3532b16960e3c090c
HIST_AFTER [0] 14126 9735c7db24ca44fee0012923934aad61c1b7cd228331db203810fde3ed49c9b2
WORK_AFTER [0] 7274 entries 559810025 bytes 16de5288493d551d90e5c5caeedf009bd604d526bf301893fd1de3b0b6ac187b
Filesystem         1B-blocks         Used    Available Use% Mounted on
/dev/sdc       1081101176832 164842184704 861266636800  17% /
D:\            1000202235904  21979668480 978222567424   3% /mnt/d
WORKTREE_LOGICAL=392255130 ALLOCATED=400297984 ENTRIES=2995
EVIDENCE_LOGICAL=106956 ALLOCATED=167936 FILES=20 SHARED_BEFORE=278192128 SHARED_AFTER=278646784
d 4096 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02
d 4096 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity
f 94 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/post-working.txt
f 566 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/preparation-guards.txt
p 0 0 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/provider.fifo
f 36 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/bridge.utc
f 925 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/paths0
f 2542 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/branch-at-parent.refs
f 2542 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/after.refs
f 2460 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/baseline.refs
f 71 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/post-historical.txt
f 2460 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/immediate.refs
f 2608 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/staged-raw0
f 138 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/invocation.argv0
f 4787 16 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/approved-checkpoint.tsv
f 2480 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/input-bindings.tsv
f 31575 64 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/provider.wire
f 2460 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/bulk.refs
f 4682 16 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/baseline.worktrees
f 2460 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/pregit.refs
f 2460 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/fast.refs
f 959 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/staged-names0
f 40651 80 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/invocation.sh.txt
d 4096 8 /home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/c05-native-v2-maintenance-20261121-02/identity/tmp
2026-11-21T06:21:17,134781656+00:00
1384.77 21712.62
FINALIZATION_TERMINAL rc=0 elapsed_centiseconds=7337 checkpoint_verified=1 build_verified=1
~~~~~

END RECEIPT
