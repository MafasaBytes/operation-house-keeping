# ST-001 Slice D Pre-Append Rehearsal Results

Date: 2026-08-31

Status: exact non-authoritative candidate reproduced; stopped at owner gate

## 1. Concise result

The frozen candidate is one neutral synthetic state anchor, one SRG, and one
parentless STD. Four independent reproduction columns generated identical
candidate record bytes, query serializations, and disclosure artifact bytes.

The authoritative demo ledger remains exactly 32 records at
`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`,
with zero committed SRG, STD, or STW records. Nothing was appended, pushed, or
merged.

These are the corrected results. The earlier manifest's fields named
canonical were derived from Pydantic JSON-mode output and therefore used `Z`
for the only UTC timestamp. Every canonical value below now comes directly
from the model kernel's normative canonical functions, uses `+00:00`, and is
covered by record-ID verification assertions.

## 2. Exact candidate anchor

```json
{
  "anchor_id": "sta_ec739d80d5a843d28a91f4cf96de3883",
  "display_name": "Synthetic Region Alpha",
  "namespace": "demo-printer",
  "role_name": null
}
```

The public UUID4 minter allocation is frozen in the existing manifest. The
minter was not called during recovery, rehearsal, or any reproduction column.

## 3. Exact record identities and byte contracts

Append order is SRG first, STD second.

| Record | Canonical payload bytes | Canonical payload SHA-256 | Stored bytes | Stored-file SHA-256 |
|---|---:|---|---:|---|
| `srg_ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a` | 1012 | `ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a` | 1278 | `a0056abafdb5ad51496952721bec4d8eb7ff4a8b562f168c693ab8cd2f964781` |
| `std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0` | 1169 | `d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0` | 1474 | `5dbc8c57e6dd91a987b1fef7373d6864d20786d19751bc6a822a84dec9574ea6` |

SRG semantic contract:

- subject entity:
  `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`;
- permanent condition:
  `con_4b768cf843f5474cb5e564e31d239a59`;
- family: `all_of_constraints`;
- authority: `test_fixture / st001_demo_fixture / manual_declaration`;
- recorded at: `2026-08-31T12:00:00+00:00`;
- note: `ST-001 bounded synthetic state registration.`

STD semantic contract:

- state anchor:
  `sta_ec739d80d5a843d28a91f4cf96de3883`;
- context: `lifecycle_view / as_operated`;
- exact VCN pin:
  `vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`;
- basis: `independent_latest_at_or_before_cutoff`;
- parents: none;
- authority: `test_fixture / st001_demo_fixture / manual_declaration`;
- recorded at: `2026-08-31T12:01:00+00:00`;
- note: `ST-001 bounded synthetic state declaration.`

The complete authority, evidence, notes, canonical payloads, records, stored
JSON, and hashes are frozen verbatim in the manifest.

## 4. Exact proposed 34-record membership

```text
bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e
brg_1fd13b69377257d987775c56f7abf9eedd466d4ca6555ff33ba6b8cf6e815d5e
crg_870fe60d91056b6b1da9e3f734e5156cbb52722f6a0fc5f366f66cd40102a3df
pcm_cb590cba8f33cc49ca6b2d22ef222606f9cc2f1117a8b60f1086099b6cd0337d
pcn_4861ecf058add8a45686c9b9c4f2e28085f60575705d6d06f1890b8ef11f1726
pif_258ca8416b648b6d1fa4e89f9b482ebc23ac761d275992cd82f0a89062213242
pif_80ce1f623bcec03fa2de7d6a40828a779d9005198b6629bb1839f3cf41e63e84
pif_bd6972d529c96a1cf0f19c9876b0703d8e9335e7ae374006b9ecbd63b1a3cdd0
pif_e4fb4c31e5ce7d9530a42107b552acfede86d0d55f066fa8c43d1f813d7a3abf
pif_ee957851ecd834be8a4db14a5c0bc25070a1b2987979f6519ca28ab7bfb8ff70
pif_f914972ae11f391fe17ff42a0521c02eca08d1d61072afc1eb684ed0e9792717
prg_c06e49bef910d073a6af206d884a1bb68c0b9baa1cdb1d698d0c35c61025e057
prg_c37057871b41bf873e317abde29dbba764be4974e195e21261d26942e5833af9
reg_5776a541a04b428f35af40203294a34a8a9978f0bdf3572a8745e6febddd5941
reg_9b5491aaa131b0df070cee792c83e002bdc4232cbbaba443f967cd3e5b780451
reg_a502243be0cb229ab386f20db6803e01329dcdd5a22f8e922f1a92555a7ba0ba
reg_c17de916b41ab5f6bcdf4165f47da1d604689e1eafa9afc31ea99092eacbcc90
reg_c7ad4c326425439d5e2bff4d0a3dc42cf26540514ecc015d060c711943ff92c5
rel_12a2812d151da28579784518b619a2a577318a977911bcaf27093d9263d044fa
rel_2978509392132152b2d74beb139d2f85e8508f6c50e6ebfea996cd7c78fcf0d5
rel_3c5a723282c6fc05cd694e5a98e208840e1d897f80dc29a524c0b8d35ff34d5a
rel_a1fef969809045884d29a981df43bce332b9a8871bd2236cd1d430fd53e31a47
rtd_04b8da45255190340e7366ce2a373a9b402dc32eb86b6312f382f5e37a4e81b7
rtd_5330e9966910b66a2a64380a39c190e12bc3649e8192f47b2358c6a13331f2f9
rtd_a21999304a0a5458eef47b82cd06a8c055aa83d2aa90bb8b17d93590c3487f06
srg_ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a
std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0
vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec
vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49
vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6
vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7
vsm_053882a4714f51a0e9d358b5a8598cfca856482d9af9acd0117313a9ab8d1c40
vsm_3b4b829006033604f088f2ff0e2727f4b2a1987f7d0edc5be54327562ef8791b
vsp_c8e5d91d38c5e3f36d0d592737aac5ce26c03eb5d169365c38953f971ff62ba0
```

The proposed revision is:

`mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`

The set difference from the exact accepted 32-record membership is exactly
the SRG and STD IDs above.

## 5. Public kernel outcomes

| Query | Exact conclusion |
|---|---|
| `state()` | `registered` |
| `state_declaration()` | `declared`; `healthy`; `one_healthy_root`; one root |
| `states_of_entity()` | registered subject; exactly one candidate entry |
| `state_assertion(SRG)` | `found`; permanent/event-shaped disclosure |
| `state_assertion(STD)` | `found`; `current`; containing lineage `healthy` |

There is one registration, one declaration, one parentless root, one current
tip, zero withdrawals, zero correction descendants, zero forks, and zero
second roots.

## 6. Direct CN evidence and complete ST result

Exact source selector:

```json
{
  "property": {
    "extraction_route": "api:moonraker:v1",
    "item_key": "printer_objects",
    "json_pointer": "/result/status/extruder/temperature"
  },
  "subject": {
    "adapter_id": "moonraker",
    "source_id": "printer-1",
    "subject_identifier": "extruder"
  }
}
```

Exact cutoff: `2026-08-07T20:30:00+00:00`.

Direct CN:

- constraint status: `declared`;
- current declaration:
  `vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`;
- observed canonical decimal: `60.4`;
- predicate: inclusive upper bound `80`;
- verdict: `satisfied`.

Complete ST summary:

- state: `declared`;
- lineage: `healthy`;
- declaration alignment: `exact_current`;
- condition outcome: `satisfied`;
- coverage: `complete`;
- temporal alignment: `not_asserted`;
- execution: `executed`;
- refusals: none;
- computed match: `matches`.

The occurrence was received at `2026-08-07T20:00:18Z`, with occurrence ID
`cd2579c5bca1c1f71f0170eaa73c74fb`, raw record ID
`698aa72a05a317e62b62274ffcb3bbfb`, and payload checksum
`sha256:6771710d0a97db795a53192e1c6d463937deaa8c11e6fce3d35285d69114caf2`.

Provenance axes remain separate:

- model revision:
  `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`;
- binding revision:
  `rev_67af9095cb5a75fc9022b7666a9a68d1eed48f03750f8e26759b745240e60b93`;
- interpretation revision:
  `irv_6b65d609f8074091e1e09aee99c8b4a0360ecacd672ff99ede5a076c2b3cd57f`;
- temporal cutoff: `2026-08-07T20:30:00+00:00`;
- declaration recorded at: `2026-08-31T12:01:00+00:00`.

The later declaration is applied relative to evidence at the cutoff. This is
not a claim that the declaration existed at the cutoff or that the observation
persisted.

## 7. Candidate artifact and manifest

| Owner-gate file | Bytes | SHA-256 |
|---|---:|---|
| candidate identities manifest | 31834 | `990807c2b81ad4a8ec256869bdb5271bf54b360132ca3ab063d5e837bcde43f7` |
| candidate disclosure | 510943 | `23baf7961570aa1eca4c3a7b08e19673c69cfbc53a61e912d86a887f775ef7b9` |

The manifest's embedded canonical-content SHA-256 is
`4a3e6826637d932e5c0234eb9b5c2a3c7397f475bad0de0e88524def50782c3c`.

The disclosure contains the exact 32- and 34-record memberships; separate
model, binding, interpretation, and temporal axes; both candidate records and
their evidence; complete kernel disclosures; direct CN result; complete ST
result; occurrence timing and provenance; predecessor hashes; accepted
PT/VP/BH hashes; raw-authenticity limitation; warnings; and disclaimer.

## 8. Reproduction-column equality

| Column | Frozen manifest only | Reproduction serialization | Artifact |
|---|---|---|---|
| disposable root 1 | yes | 485765 bytes / `7b2dcbe05108824b0a940ddd65984f49cb44ab599c9a47c0b75b8faed71d2296` | exact |
| disposable root 2, reverse predecessor copy | yes | byte-identical | exact |
| fresh base-only clean checkout | yes | byte-identical | exact |
| fresh all-extras clean checkout | yes | byte-identical | exact |

Equality covers the complete anchor, canonical payloads, stored-file bytes,
record IDs, hashes, append order, membership, revision, all query disclosures,
direct CN serialization, complete ST serialization, artifact bytes,
predecessor aggregate, and accepted artifact hashes. No reproduction invoked
the minter.

## 9. Predecessor and accepted-artifact preservation

- accepted predecessor records: 32;
- accepted predecessor revision:
  `mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`;
- predecessor file-map aggregate:
  `eb0b50157837ff33d0f1d67c595ab96c29cd45c61254566da07493622fa69c58`;
- protected-tree aggregate:
  `c39c52cb251d593d8201acaf61bc6bac36839c79dae22466b1bb7e22fc571e08`;
- PT artifact: 33855 bytes,
  `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`;
- VP artifact: 17824 bytes,
  `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`;
- BH artifact: 122406 bytes,
  `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`.

Explicit historical replay passed for 9, 10, 11, 14, 16, 18, 28, 29, and 32
records. Every historical result disclosed candidate-state absence. All
predecessor bytes remained unchanged before and after every rehearsal.

## 10. Verification counts

| Verification | Result |
|---|---:|
| focused candidate rehearsal | 12 passed |
| direct public kernel/CN/ST demonstration | passed inside every rehearsal column |
| deterministic four-column comparison | exact byte equality |
| explicit 9/10/11/14/16/18/28/29/32 replay | 9 memberships passed |
| implementation-worktree repository suite | 3076 passed |
| fresh base-only aggregate | 3028 passed, 35 expected skips, 1 sandbox-denied setup |
| fresh base-only isolated permitted loopback | 1 passed |
| fresh base-only distinct verified total | 3029 passed, 35 expected skips |
| fresh all-extras aggregate | 3063 passed, 1 sandbox-denied setup |
| fresh all-extras isolated permitted loopback | 1 passed |
| fresh all-extras distinct verified total | 3064 passed |
| focused OCP/STEP/PDF | 79 passed |
| backend compilation | passed |
| working-tree whitespace | passed |
| full milestone-range whitespace | passed |

The two aggregate errors were only the sandbox-denied loopback server setup.
The exact test passed separately in each clean checkout with permission.

## 11. Git status and topology

- branch: `st001`;
- accepted Slice C HEAD:
  `f2c6e4e12c3004615e3b0a6f321f6c2b3edec7d6`;
- current committed HEAD:
  `2f51abe7ffbef473cc9265b7bac62488974b3a01`;
- local `origin/main` relation: 40 commits ahead, 0 behind;
- branch upstream: none;
- pushes: none;
- merges: none;
- rebases, resets, cherry-picks, amends, and history rewrites: none.

Two pre-existing administrative boundary commits follow Slice C:

1. `70d35981b7552d3c2af14dddee34c9fb6eeb0752` — records acceptance;
2. `2f51abe7ffbef473cc9265b7bac62488974b3a01` — makes continued append
   prohibition explicit.

No tracked file is modified. The exact untracked files at the owner gate are:

```text
docs/superpowers/reports/2026-08-31-st001-slice-d-candidate-disclosure.json
docs/superpowers/reports/2026-08-31-st001-slice-d-candidate-identities.json
docs/superpowers/reports/2026-08-31-st001-slice-d-preappend-integrity-correction-report.md
docs/superpowers/reports/2026-08-31-st001-slice-d-preappend-rehearsal-report.md
docs/superpowers/reports/2026-08-31-st001-slice-d-preappend-rehearsal-results.md
tests/model_kernel/st001_slice_d_rehearsal.py
tests/model_kernel/test_st001_slice_d_preappend_rehearsal.py
```

The candidate manifest, candidate disclosure, and reports are not committed.
No candidate SRG or STD record file is present in the authoritative ledger.

## 12. Limitations and mandatory disclaimer

Names, shared ownership, hierarchy, CAD, ports, VPA, PIF/PCN/PCM, BH
declarations, semantic compatibility, CN satisfaction alone, temporal
correlation, and observation changes did not create the state. Displaying an
observation beside a state does not persist it as state truth.

ST proves the internal coherence of carried public results and does not
independently authenticate uncaptured raw payload bytes.

> This is an illustrative synthetic ST-001 state declaration and evidence classification fixture. `matches` means only that the explicitly selected admitted observation satisfied the referenced synthetic constraint under the stated context, cutoff, and revisions. It does not claim that a real printer is currently in this state, that the state is exclusive or complete, that any transition occurred, or that temporal order establishes cause, control, safety, health, diagnosis, correctness, or recommended action.

## 13. Owner question

Does the owner approve this exact frozen candidate contract and separately
authorize the authoritative 32-to-34 Slice D append?
