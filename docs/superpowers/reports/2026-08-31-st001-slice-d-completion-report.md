# ST-001 Slice D Authoritative Append Completion Report

Date: 2026-08-31

Status: implemented and verified; final ST-001 owner acceptance pending.

## 1. Authorization and scope

The owner approved the exact corrected frozen candidate contract and
separately authorized the authoritative 32-to-34 record append. The append was
performed through the public builders and `ModelStore`, in the only authorized
order:

1. `srg_ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a`
2. `std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0`

No minter was invoked. The frozen `StateAnchor` was reconstructed from the
approved manifest. No substitution, additional record, correction,
withdrawal, fork, second root, family, transition record, or other ledger
mutation occurred.

The local implementation commit is
`0f05903af4f11fd94d6e6987247ceb9795faebd6` (`feat: append approved ST-001
state fixture`). Nothing was pushed, merged, rebased, reset, cherry-picked,
amended, or history-rewritten.

## 2. Exact authoritative contract

| Item | Exact value |
|---|---|
| StateAnchor | `sta_ec739d80d5a843d28a91f4cf96de3883` |
| SRG | `srg_ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a` |
| STD | `std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0` |
| predecessor count | 32 |
| predecessor revision | `mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b` |
| authoritative count | 34 |
| authoritative revision | `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41` |
| predecessor file-map aggregate | `eb0b50157837ff33d0f1d67c595ab96c29cd45c61254566da07493622fa69c58` |
| authoritative 34-file aggregate | `cf3a534b4b7d13a85fb1f23a3e81881b03e084fc508145950cbc8618f247d6cd` |

The two authoritative stored files retain the approved contract:

| Record | Kernel canonical bytes | Kernel canonical SHA-256 / ID suffix | Stored bytes | Stored SHA-256 |
|---|---:|---|---:|---|
| SRG | 1012 | `ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a` | 1278 | `a0056abafdb5ad51496952721bec4d8eb7ff4a8b562f168c693ab8cd2f964781` |
| STD | 1169 | `d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0` | 1474 | `5dbc8c57e6dd91a987b1fef7373d6864d20786d19751bc6a822a84dec9574ea6` |

For both records, disclosed canonical bytes equal
`backend.model_kernel.canonical.canonical_bytes(record)`, canonical SHA-256
equals the record-ID suffix, `compute_record_id(record)` equals the frozen ID,
and `verify_record_id(record)` is true. Normative UTC canonical timestamps use
`+00:00`.

## 3. Exact current membership

The authoritative membership is exactly:

- `bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e`
- `brg_1fd13b69377257d987775c56f7abf9eedd466d4ca6555ff33ba6b8cf6e815d5e`
- `crg_870fe60d91056b6b1da9e3f734e5156cbb52722f6a0fc5f366f66cd40102a3df`
- `pcm_cb590cba8f33cc49ca6b2d22ef222606f9cc2f1117a8b60f1086099b6cd0337d`
- `pcn_4861ecf058add8a45686c9b9c4f2e28085f60575705d6d06f1890b8ef11f1726`
- `pif_258ca8416b648b6d1fa4e89f9b482ebc23ac761d275992cd82f0a89062213242`
- `pif_80ce1f623bcec03fa2de7d6a40828a779d9005198b6629bb1839f3cf41e63e84`
- `pif_bd6972d529c96a1cf0f19c9876b0703d8e9335e7ae374006b9ecbd63b1a3cdd0`
- `pif_e4fb4c31e5ce7d9530a42107b552acfede86d0d55f066fa8c43d1f813d7a3abf`
- `pif_ee957851ecd834be8a4db14a5c0bc25070a1b2987979f6519ca28ab7bfb8ff70`
- `pif_f914972ae11f391fe17ff42a0521c02eca08d1d61072afc1eb684ed0e9792717`
- `prg_c06e49bef910d073a6af206d884a1bb68c0b9baa1cdb1d698d0c35c61025e057`
- `prg_c37057871b41bf873e317abde29dbba764be4974e195e21261d26942e5833af9`
- `reg_5776a541a04b428f35af40203294a34a8a9978f0bdf3572a8745e6febddd5941`
- `reg_9b5491aaa131b0df070cee792c83e002bdc4232cbbaba443f967cd3e5b780451`
- `reg_a502243be0cb229ab386f20db6803e01329dcdd5a22f8e922f1a92555a7ba0ba`
- `reg_c17de916b41ab5f6bcdf4165f47da1d604689e1eafa9afc31ea99092eacbcc90`
- `reg_c7ad4c326425439d5e2bff4d0a3dc42cf26540514ecc015d060c711943ff92c5`
- `rel_12a2812d151da28579784518b619a2a577318a977911bcaf27093d9263d044fa`
- `rel_2978509392132152b2d74beb139d2f85e8508f6c50e6ebfea996cd7c78fcf0d5`
- `rel_3c5a723282c6fc05cd694e5a98e208840e1d897f80dc29a524c0b8d35ff34d5a`
- `rel_a1fef969809045884d29a981df43bce332b9a8871bd2236cd1d430fd53e31a47`
- `rtd_04b8da45255190340e7366ce2a373a9b402dc32eb86b6312f382f5e37a4e81b7`
- `rtd_5330e9966910b66a2a64380a39c190e12bc3649e8192f47b2358c6a13331f2f9`
- `rtd_a21999304a0a5458eef47b82cd06a8c055aa83d2aa90bb8b17d93590c3487f06`
- `srg_ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a`
- `std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0`
- `vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`
- `vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49`
- `vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6`
- `vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7`
- `vsm_053882a4714f51a0e9d358b5a8598cfca856482d9af9acd0117313a9ab8d1c40`
- `vsm_3b4b829006033604f088f2ff0e2727f4b2a1987f7d0edc5be54327562ef8791b`
- `vsp_c8e5d91d38c5e3f36d0d592737aac5ce26c03eb5d169365c38953f971ff62ba0`

The set difference from the explicit 32-record predecessor is exactly the SRG
and STD above. There is one SRG, one STD, and zero STW records.

## 4. Public demonstrations

Direct public kernel results at the authoritative revision are:

- `state()` -> `registered`;
- `state_declaration()` -> `declared`, `healthy`,
  `one_healthy_root`;
- `states_of_entity()` -> one exact candidate entry;
- `state_assertion(SRG)` -> `found`, permanent/event-shaped disclosure;
- `state_assertion(STD)` -> `found`, `current`, healthy containing lineage.

At the exact cutoff `2026-08-07T20:30:00+00:00`, the public CN facade selects
the admitted occurrence received at `2026-08-07T20:00:18Z`, preserves its
individual provenance, canonicalizes its observed value as `60.4`, applies the
exact-current VCN
`vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`,
and returns `satisfied` for inclusive upper bound `80`.

The complete ST result is:

- state conclusion: `declared`;
- lineage: `healthy`;
- declaration alignment: `exact_current`;
- condition outcome: `satisfied`;
- condition coverage: `complete`;
- temporal alignment: `not_asserted`;
- execution: `executed`;
- refusals: none;
- computed match: `matches`.

The later model declaration is applied relative to evidence at the cutoff.
This does not claim that the declaration existed at the cutoff or that the
observation persisted.

## 5. Frozen owner-gate artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| corrected candidate identities manifest | 31834 | `990807c2b81ad4a8ec256869bdb5271bf54b360132ca3ab063d5e837bcde43f7` |
| deterministic candidate disclosure | 510943 | `23baf7961570aa1eca4c3a7b08e19673c69cfbc53a61e912d86a887f775ef7b9` |

The disclosure remains the approved pre-append artifact. Its
`authoritative_append_performed=false` field truthfully describes that frozen
artifact's generation scope; it was not rewritten after the append.

Two newly initialized disposable roots, including reversed predecessor copy
order, and both clean-checkout columns independently reproduced:

- reproduction serialization: 485765 bytes;
- reproduction SHA-256:
  `7b2dcbe05108824b0a940ddd65984f49cb44ab599c9a47c0b75b8faed71d2296`;
- exact 34-record revision:
  `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`;
- exact 510943-byte disclosure and SHA-256 above.

No reproduction invoked `mint_state_anchor()` or copied candidate record files
between roots.

## 6. Preservation

Every frozen predecessor hash in the manifest still matches its authoritative
file. Explicit historical replay remains exact for 9, 10, 11, 14, 16, 18, 28,
29, and 32 records. The 32-record revision continues to disclose candidate
state absence.

Accepted artifact preservation is exact:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| PT | 33855 | `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8` |
| VP | 17824 | `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3` |
| BH | 122406 | `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3` |

Bindings, interpretations, temporal/source fixtures, structural fixtures, and
accepted showcase artifacts were not modified by the append.

## 7. Verification results

| Verification | Result |
|---|---:|
| focused authoritative/rehearsal/kernel/CN/ST suite | 177 passed |
| implementation-worktree complete repository suite | 3083 passed |
| fresh base-only aggregate | 3047 passed, 35 expected optional skips, 1 sandbox-denied loopback setup |
| fresh base-only permitted loopback rerun | 1 passed |
| fresh base-only distinct verified total | 3048 passed, 35 expected optional skips |
| fresh all-extras aggregate | 3082 passed, 1 sandbox-denied loopback setup |
| fresh all-extras permitted loopback rerun | 1 passed |
| fresh all-extras distinct verified total | 3083 passed |
| focused OCP/STEP/PDF paths | 120 passed |
| backend compilation, base-only | passed |
| backend compilation, all-extras | passed |
| clean-column reproduction equality | exact |
| working-tree `git diff --check` before report | passed |
| full milestone-range `git diff --check` | passed |

Both clean columns were detached at
`0f05903af4f11fd94d6e6987247ceb9795faebd6`, had empty Git status, and were
removed only after their resolved paths were confirmed.

## 8. Mandatory limitation

> This is an illustrative synthetic ST-001 state declaration and evidence classification fixture. `matches` means only that the explicitly selected admitted observation satisfied the referenced synthetic constraint under the stated context, cutoff, and revisions. It does not claim that a real printer is currently in this state, that the state is exclusive or complete, that any transition occurred, or that temporal order establishes cause, control, safety, health, diagnosis, correctness, or recommended action.

Names, shared ownership, hierarchy, CAD, ports, VPA, PIF, PCN, PCM, BH
declarations, semantic compatibility, CN satisfaction alone, temporal
correlation, and observation changes did not create the state. Displaying an
observation beside a state does not persist it as state truth. ST proves the
internal coherence of carried public results and does not independently
authenticate uncaptured raw payload bytes.

## 9. Git state and owner gate

- branch: `st001`;
- HEAD: `0f05903af4f11fd94d6e6987247ceb9795faebd6`;
- relation to local `origin/main`: 43 commits ahead, 0 behind;
- branch upstream: none;
- modified tracked files after this report: none;
- untracked files after this report: only
  `docs/superpowers/reports/2026-08-31-st001-slice-d-completion-report.md`;
- pushed: no;
- merged: no.

Owner question: Do you grant final ST-001 owner acceptance for the exact
authoritative 34-record contract, implementation commit, frozen artifacts,
public query/classification disclosures, and preservation/verification results
recorded above?
