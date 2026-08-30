# BH-001 Slice D pre-append rehearsal results

## 1. Outcome and owner gate

The narrowly scoped public `mint_variable_anchor()` repair is committed and
green. The two candidate anchors were then allocated exactly once, frozen in a
canonical manifest, reconstructed through their public contracts, and used in
two independently created disposable model ledgers. Both rehearsals produced
byte-identical candidate record files and disclosure artifacts.

No authoritative ledger append has occurred. The accepted demo model remains
29 records at
`mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652`.
This report presents the exact candidate identities and artifact contract for
owner approval. It does not authorize or perform the Slice D authoritative
append.

## 2. Authority, branch, and commits

- Branch: `bh001`
- Administrative starting HEAD:
  `a619ed14d36aeb508e4db8602adbbdce4b1b4e2d`
- Current committed HEAD:
  `2bee0f3808335d57d5d835f66892d1c21004d519`
- Remote relation, using existing local `origin/main`: 32 commits ahead and 0
  behind; branch has no configured upstream.
- No push, merge, rebase, reset, cherry-pick, amend, or history rewrite was
  performed.

Commits created under this owner decision:

1. `d637adb0a6dc10030ba8236e0e8cc5180654d73a`
   — `docs: resolve BH-001 Slice D minter gate`
2. `b77cb1c9077e30a80b4342a7d61e891e94e486be`
   — `docs: harden BH-001 rehearsal identity gate`
3. `2bee0f3808335d57d5d835f66892d1c21004d519`
   — `feat: add public variable anchor minter`

The first two commits preserve the original fail-closed discrepancy and record
its owner resolution in the specification, ADR, plans, matrix, status docs, and
focused documentation assertions. The third is the separately committed,
bounded production addition.

## 3. Public variable-anchor minter

The committed public API is exactly:

```python
def mint_variable_anchor(
    *,
    entity_anchor_id: str,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> VariableAnchor:
    ...
```

It calls standard-library `uuid4()` once, uses `uuid4().hex`, prefixes the
result with `var_`, and constructs the existing `VariableAnchor`. It performs
no I/O, storage, registration, binding, persistence, authority assertion, or
model-record construction. It adds only `mint_variable_anchor` to the ordered
system-identity public surface, immediately after `mint_port_anchor`. Existing
anchor contracts, minters, canonical identities, and golden vectors are
unchanged.

Red-first evidence recorded during implementation:

- Before implementation: `22 failed, 83 passed in 3.49s`.
- Focused green: `105 passed in 1.57s`.
- Identity/canonical affected green: `321 passed in 15.46s`.
- Expanded focused/canonical/architecture green:
  `163 passed in 17.92s`.

## 4. Frozen candidate manifest

Path:

`docs/superpowers/reports/2026-08-30-bh001-slice-d-candidate-identities.json`

- Status: `non_authoritative_candidate`
- Bytes: `678`
- SHA-256:
  `8524e9219ee7e1e452d7390f00df99c790bc8d91068e04fc4ec4f7463f75ea07`
- Accepted base revision:
  `mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652`

The variable minter was invoked exactly once and then the behavior minter was
invoked exactly once. Neither has been invoked again. The manifest contains no
timestamp, machine path, random seed, or runtime metadata. Both complete
anchor mappings revalidate through the existing public contracts as RFC-4122
UUID version 4 identities.

Frozen candidate variable anchor:

```json
{
  "anchor_id": "var_ab2d312466054c20b0ac764e9bc0114e",
  "display_name": "Synthetic comparison variable",
  "entity_anchor_id": "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50",
  "namespace": "demo-printer",
  "role_name": null
}
```

Frozen candidate behavior anchor:

```json
{
  "anchor_id": "bhv_80e21f1682e449ca9c65a5e2ee051ea0",
  "display_name": "Synthetic exact numeric equality",
  "namespace": "demo-printer",
  "role_name": null
}
```

These values are non-authoritative candidates awaiting owner approval. No
replacement candidates were minted.

## 5. Exact candidate records

All three records were constructed through public `build_record()`. Evidence
tuples, participants, and semantic locks were allowed to take their accepted
canonical ordering. The blocks below reproduce the complete stored canonical
JSON values; indentation is for review, while exact persisted bytes are pinned
by the file sizes and SHA-256 values in Section 6.

### 5.1 Candidate VariableRegistration

```json
{
  "anchor": {
    "anchor_id": "var_ab2d312466054c20b0ac764e9bc0114e",
    "display_name": "Synthetic comparison variable",
    "entity_anchor_id": "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50",
    "namespace": "demo-printer",
    "role_name": null
  },
  "authority": {
    "agent": "bh001_demo_fixture",
    "kind": "test_fixture",
    "method": "manual_declaration"
  },
  "note": "BH-001 bounded neutral synthetic participant.",
  "record_id": "vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6",
  "record_kind": "variable_registration",
  "recorded_at": "2026-08-30T12:00:00+00:00",
  "schema_version": "1"
}
```

### 5.2 Candidate BehaviorRegistration

```json
{
  "anchor": {
    "anchor_id": "bhv_80e21f1682e449ca9c65a5e2ee051ea0",
    "display_name": "Synthetic exact numeric equality",
    "namespace": "demo-printer",
    "role_name": null
  },
  "authority": {
    "agent": "bh001_demo_fixture",
    "kind": "test_fixture",
    "method": "manual_declaration"
  },
  "evidence": [
    {
      "kind": "model_record",
      "record_id": "vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6"
    },
    {
      "kind": "model_record",
      "record_id": "vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7"
    },
    {
      "kind": "owner_declaration",
      "statement": "BH-001 fixture authority explicitly registers this unordered pair of synthetic variables for the exact-numeric-equality rule family; shared ownership, names, topology, VPA associations, semantics, constraints, and observations did not create or corroborate this behavior registration."
    }
  ],
  "note": "BH-001 bounded synthetic registration.",
  "participant_variable_anchor_ids": [
    "var_ab2d312466054c20b0ac764e9bc0114e",
    "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"
  ],
  "record_id": "brg_1fd13b69377257d987775c56f7abf9eedd466d4ca6555ff33ba6b8cf6e815d5e",
  "record_kind": "behavior_registration",
  "recorded_at": "2026-08-30T12:00:00+00:00",
  "rule_family": "exact_numeric_equality",
  "schema_version": "1"
}
```

### 5.3 Candidate BehaviorRuleDeclaration

```json
{
  "authority": {
    "agent": "bh001_demo_fixture",
    "kind": "test_fixture",
    "method": "manual_declaration"
  },
  "behavior_anchor_id": "bhv_80e21f1682e449ca9c65a5e2ee051ea0",
  "context": {
    "kind": "lifecycle_view",
    "view": "as_designed"
  },
  "evaluation_basis": "same_acquisition_cohort",
  "evidence": [
    {
      "kind": "model_record",
      "record_id": "brg_1fd13b69377257d987775c56f7abf9eedd466d4ca6555ff33ba6b8cf6e815d5e"
    },
    {
      "kind": "owner_declaration",
      "statement": "BH-001 fixture authority explicitly declares this exact-numeric-equality relationship under the same-acquisition-cohort evaluation basis in the as-designed lifecycle view; illustrative declaration only, not an observed equality or real-machine behavior claim."
    }
  ],
  "note": "BH-001 bounded synthetic declaration.",
  "participant_semantics": [
    {
      "signature": {
        "observation_role": {
          "code": "synthetic_comparison",
          "system_edition": "ohk-observation-roles-1",
          "system_id": "project_local"
        },
        "quantity_kind": {
          "code": "temperature",
          "system_edition": "ohk-quantities-1",
          "system_id": "project_local"
        },
        "unit": {
          "code": "degree_celsius",
          "system_edition": "ohk-units-1",
          "system_id": "project_local"
        }
      },
      "variable_anchor_id": "var_ab2d312466054c20b0ac764e9bc0114e"
    },
    {
      "signature": {
        "observation_role": {
          "code": "measured_actual",
          "system_edition": "ohk-observation-roles-1",
          "system_id": "project_local"
        },
        "quantity_kind": {
          "code": "temperature",
          "system_edition": "ohk-quantities-1",
          "system_id": "project_local"
        },
        "unit": {
          "code": "degree_celsius",
          "system_edition": "ohk-units-1",
          "system_id": "project_local"
        }
      },
      "variable_anchor_id": "var_b7e2d3c4f5a6172839405a6b7c8d9e0f"
    }
  ],
  "record_id": "bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e",
  "record_kind": "behavior_rule_declaration",
  "recorded_at": "2026-08-30T12:00:00+00:00",
  "rule": {
    "kind": "exact_numeric_equality"
  },
  "schema_version": "1",
  "supersedes": []
}
```

The BHD owner declaration explicitly supports the context, rule, and
`same_acquisition_cohort` evaluation basis. It does not claim observed equality
or real-machine behavior.

## 6. Record files, membership, and revision

The append sequence in each disposable ledger was exactly VRG, BRG, BHD.

| Record | Stored bytes | Stored-file SHA-256 |
|---|---:|---|
| `vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6` | 630 | `0652fd7ca32de43d3e21c5a41a5117eb3c19d2a469ffa30f37b407f91937e285` |
| `brg_1fd13b69377257d987775c56f7abf9eedd466d4ca6555ff33ba6b8cf6e815d5e` | 1376 | `19068707d3bb5423eab4db189208d85749ef18cc3447135d8cfa4ea7f0e89edb` |
| `bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e` | 2333 | `fa1a40272d100eb81cc15e64cff782a654b3369a91da62bc36b1f26a2cf655cf` |

The predecessor aggregate is SHA-256 over canonical JSON containing the
sorted mapping from each of the 29 predecessor filenames to its file SHA-256,
with a final LF:

`962a4ab5551435d849739bb4cff2e5379be03424265a40d4fe4a4b8c2c7e99cf`

All 29 predecessor hashes are embedded in the candidate disclosure artifact.
Each pre/post inventory matched byte-for-byte in both runs.

The explicit candidate 32-record membership is:

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
vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec
vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49
vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6
vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7
vsm_053882a4714f51a0e9d358b5a8598cfca856482d9af9acd0117313a9ab8d1c40
vsm_3b4b829006033604f088f2ff0e2727f4b2a1987f7d0edc5be54327562ef8791b
vsp_c8e5d91d38c5e3f36d0d592737aac5ce26c03eb5d169365c38953f971ff62ba0
```

The candidate revision is:

`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`

The set difference from the explicit accepted 29-record membership is exactly
the three candidate IDs. The disposable replay has one behavior registration,
one declaration, one parentless root with one current tip, and zero BHW,
correction, fork, or second root.

## 7. Two-ledger determinism and artifact contract

Each run began from a separately created disposable root populated with the
explicit accepted 29-record membership. It used the same frozen manifest,
public anchor validation, public record builder, public `ModelStore`
append/load/replay, public Slice B queries, and public Slice C evaluator.

Run one and run two were exactly equal for:

- complete variable and behavior anchor mappings;
- all three record model contents;
- actual bytes read from all three stored files;
- record IDs, file sizes, and file hashes;
- canonical 32-record membership and final revision;
- behavior query disclosures;
- evaluator disclosure;
- all predecessor hashes and aggregate;
- binding and interpretation inventories;
- complete artifact bytes.

Additional subprocess reproductions with `PYTHONHASHSEED=1` and
`PYTHONHASHSEED=9173` produced the same contract. A guarded rehearsal copied
the 29 predecessor files in reverse order and still produced the same result.
Every append and copy destination was dynamically asserted to reside beneath
the supplied temporary root.

Candidate BH disclosure artifact:

- Bytes: `122406`
- SHA-256:
  `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`
- Schema version: `1`
- Artifact name: `BH-001 demo-printer behavior disclosure candidate`

The artifact is generated in memory only at this gate; it is not committed as
an authoritative artifact. It contains the manifest, all three complete
records, their stored-file hashes, explicit memberships and revisions, all 29
predecessor file hashes, kernel disclosures, complete evaluator result, raw
provenance, separate provenance axes, binding and interpretation inventories,
historical replay, PT/VP artifact identities, disclaimer, warnings, and a
content checksum. The test independently recomputes the content checksum from
canonical content bytes.

## 8. Kernel query disclosure

All disclosures below are direct results of the accepted public Slice B
`ModelQueries` facade over the explicit disposable 32-record membership.

Behavior registration lookup:

```text
status: registered
record_id: brg_1fd13b69377257d987775c56f7abf9eedd466d4ca6555ff33ba6b8cf6e815d5e
participants:
  - var_ab2d312466054c20b0ac764e9bc0114e
  - var_b7e2d3c4f5a6172839405a6b7c8d9e0f
```

Exact-context declaration lookup:

```text
context: lifecycle_view/as_designed
conclusion: declared
lineage_summary: healthy
agreement_findings: [one_healthy_root]
root_count: 1
root: bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e
lineage_members: [bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e]
current_tips: [bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e]
withdrawals: []
lineage_health: healthy
```

Both reverse variable queries return `status=registered` and exactly one
entry. The existing variable points to the candidate variable and the
candidate points to the existing variable; both entries disclose
`conclusion=declared`, `lineage_summary=healthy`, and
`agreement_findings=[one_healthy_root]`.

Assertion disclosure:

- BRG lookup is `found`; as a permanent registration it has no activity,
  lineage health, root, successor, or withdrawal fields.
- BHD lookup is `found`, activity is `current`, containing lineage health is
  `healthy`, containing subject conclusion is `declared`, the containing root
  is the BHD itself, and successor and withdrawal tuples are empty.

The explicit accepted 29-record replay returns:

```text
behavior registration: not_registered
exact-context declaration conclusion: not_registered
existing variable reverse query: registered, zero entries
candidate BRG assertion: not_found
candidate BHD assertion: not_found
```

No name, ownership, VPA, port, topology, compatibility, semantic, constraint,
or observation evidence created a behavior query row.

## 9. Evidence-gated evaluator disclosure

The public Slice C evaluator was invoked with exactly two explicit participant
selectors. The candidate variable uses the neutral property locator
`synthetic:bh001:v1 / bh001_candidate /synthetic/comparison-variable`; the
existing variable uses the accepted Moonraker temperature selector. No source
discovery, candidate cross-product, or implicit selection occurred.

Outer result:

```text
execution: not_executed
computed_relation: null
cohort_admission: not_evaluated
```

Candidate participant, index 0:

```text
variable_anchor_id: var_ab2d312466054c20b0ac764e9bc0114e
model_admission: admitted
observation_availability: none_before_cutoff
attachment_admission: not_evaluated
semantic_admission: not_evaluated
unit_admission: not_evaluated
lock_admission: not_evaluated
numeric_admission: not_evaluated
admission: not_admitted
canonical_decimal: null
refusal_reasons:
  - observation_absent
  - numeric_specification_not_available
  - model_quantity_kind_not_available
  - model_observation_role_not_available
```

Existing participant, index 1:

```text
variable_anchor_id: var_b7e2d3c4f5a6172839405a6b7c8d9e0f
model_admission: admitted
observation_availability: observed
attachment_admission: attached
semantic_admission: admitted
unit_admission: exact
lock_admission: matched
numeric_admission: not_evaluated
admission: not_admitted
refusal_reasons: []
canonical_decimal: null
```

The aggregate ordered refusal rows are precisely the four candidate-local
reasons above. The existing participant retains its independently available
observation and accepted lower-layer findings; the absent candidate evidence
does not erase it. Cohort admission is `not_evaluated` because one selected
occurrence is absent. The numeric parser is not used and no relation is
computed.

Direct-equivalence checks passed:

- each nested semantic result equals the result of its direct public semantic
  query;
- each nested variable state equals the state carried by that direct semantic
  result and the corresponding direct state query;
- the selected existing occurrence equals the direct temporal latest-observed
  result.

Existing participant occurrence and raw provenance:

```text
value_json: 60.4
received_at: 2026-08-07T20:00:18+00:00
occurrence_id: cd2579c5bca1c1f71f0170eaa73c74fb
attempt_id: 971cf9dd7a595e13c5a74ba505ad92be
observation_id: 297be88ea705222d9b03b97733276774
raw_record_id: 698aa72a05a317e62b62274ffcb3bbfb
payload_checksum: sha256:6771710d0a97db795a53192e1c6d463937deaa8c11e6fce3d35285d69114caf2
```

Provenance axes remain separate:

```text
model_revision: mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b
binding_revision: rev_67af9095cb5a75fc9022b7666a9a68d1eed48f03750f8e26759b745240e60b93
interpretation_revision: irv_6b65d609f8074091e1e09aee99c8b4a0360ecacd672ff99ede5a076c2b3cd57f
temporal_cutoff: 2026-08-07T20:30:00+00:00
```

No shared validity interval, clock synchronization, physical simultaneity, or
behavioral truth is claimed.

## 10. Binding-seam proof

The candidate variable is the sole pinned exception to the committed binding
declaration seam:

```text
candidate variable: var_ab2d312466054c20b0ac764e9bc0114e
candidate VRG: vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6
binding AnchorDeclaration present: false
model-state anchor_agreement: binding_declaration_absent
pre-existing declared anchors checked: 6
pre-existing anchors exact: true
second undeclared variable rejected: true
divergent candidate rejected: true
stale-ID model_copy candidate rejected: true
stale-ID model_construct candidate rejected: true
```

Both committed binding sets retained their exact memberships, revisions, and
bytes:

- `bindings/demo-printer`: 6 records,
  `rev_67af9095cb5a75fc9022b7666a9a68d1eed48f03750f8e26759b745240e60b93`
- `bindings/demo-printer-model`: 5 records,
  `rev_bf16a154f7ab89a0e820f5d2917bf1e7361d24381d10c9c208e6092846532d99`
- Combined 11-file inventory aggregate:
  `cae11d75c971363852adf4bf4470b3354316652eacbf6d9ed5882404e8b12cda`

No binding `AnchorDeclaration` or assertion is proposed or written.

## 11. Historical and byte preservation

The following existing explicit memberships replayed without reconstruction
from directory enumeration:

| Records | Revision |
|---:|---|
| 9 | `mrv_c28b6301f712f94249e6ccea87f1cfd4f9c04c1cc00fef3ae3d023e3da83227f` |
| 10 | `mrv_105658072294bad92f83e3d536863cb46d6d7ae83f271fb59d5026839d002686` |
| 11 | `mrv_25afc0ebf17ed12bd6ef0a95795798a53ef2731983410136d3da15c4d0f98093` |
| 14 | `mrv_702c840f7da00617feb1be252838105d8b001b2e19978842bdcbec56996c99ff` |
| 16 | `mrv_23631989f98b678aaf1c556c345ac57a320ec266c2f712a40099e8032ca8135b` |
| 18 | `mrv_919e1b36216243fd211e38a9d36556afa0d46e3660c381302d271ec1fb258c51` |
| 28 | `mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2` |
| 29 | `mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652` |

Before, between, and after both rehearsals, the following authoritative tree
inventories were equal:

| Scope | Files | Inventory aggregate SHA-256 |
|---|---:|---|
| accepted model ledger | 29 | `962a4ab5551435d849739bb4cff2e5379be03424265a40d4fe4a4b8c2c7e99cf` |
| both binding sets | 11 | `cae11d75c971363852adf4bf4470b3354316652eacbf6d9ed5882404e8b12cda` |
| interpretation set | 3 | `819a21911a227c1175d6a5552ba924806e1ee0d13ae75009c4b789db979c83fd` |
| committed raw store | 5 | `16ff9454f9e13cbbcb5be687d0fcbc029d80c556bd51728c6ef025f78e71d91a` |
| structural showcase | 9 | `dd7d8c986d769dcec519b7422cad417d6c3cdd39252dcd686c8c2a4a225d45ce` |

The interpretation revision remains
`irv_6b65d609f8074091e1e09aee99c8b4a0360ecacd672ff99ede5a076c2b3cd57f`.

The existing artifacts were regenerated inside every rehearsal:

- PT: 33,855 bytes,
  `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`
- VP: 17,824 bytes,
  `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`

The approved VPA file remains at SHA-256
`95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e`.
The authoritative model directory contains exactly 29 JSON files and none of
the candidate VRG, BRG, or BHD files exists there.

## 12. Adversarial review and repairs

The backend, test, and final-integrity specialists reviewed the corrected
rehearsal, not the superseded first draft. The accepted repairs were:

1. The BHD claim-bearing statement was strengthened to evidence the exact
   `same_acquisition_cohort` basis as well as the rule and context. This
   intentionally changed the candidate BHD ID, its file hash, final revision,
   and artifact hash before owner presentation.
2. A private canonical serializer import and duplicated stored-byte encoder
   were removed. The gate now relies on actual public-`ModelStore` outputs,
   public replay equality, direct cross-ledger raw-byte comparison, and pinned
   file hashes. AST coverage prohibits private kernel-module imports.
3. The binding-seam oracle now compares the complete exact candidate VRG,
   closing a stale-record-ID substitution gap. Both `model_copy` and
   `model_construct` attacks fail.
4. Hash-seed subprocesses, reversed predecessor order, dynamic append/copy
   destination guards, inner artifact-checksum recomputation, and protected
   raw/structural inventories were added.
5. PT and VP artifacts are regenerated and verified before their accepted
   identities enter the candidate BH artifact.

Final specialist verdicts are green. Reviewers made no edits, invoked no
minter, and appended no store.

## 13. Verification evidence

Key commands use `PYTHONDONTWRITEBYTECODE=1`, disable repository pytest
addopts, and disable the cache provider.

Public minter and documentation surface:

```text
.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/identity_binding/test_variable_anchor_minter.py \
  tests/identity_binding/test_behavior_anchor.py \
  tests/identity_binding/test_port_anchor.py \
  tests/model_kernel/test_behavior_slice_d_rehearsal_documentation.py -q

71 passed in 1.93s
```

Focused disposable rehearsal gate:

```text
.venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_bh001_slice_d_preappend_rehearsal.py -q

13 passed in 63.32s
```

That focused count includes both independent ledgers, two hash-seed
subprocesses, reversed predecessor order, dynamic destination guards, exact
queries/evaluator, hostile seam attacks, explicit histories, and artifact
regeneration.

Affected BH/model/state regression command covered the rehearsal gate, all BH
record/query/evaluator tests, cross-layer seam, demo histories, PT/VP queries
and artifacts, and behavior-anchor identity tests:

```text
344 passed in 175.53s
```

The complete repository suite result is recorded after the command completes
in Section 16 below.

Other checks:

- `git diff --check`: pass.
- Python compilation of the rehearsal helper: pass.
- Both candidate UUIDs revalidate as RFC-4122 version 4 with the correct
  variant bits.
- Authoritative model load: 29 records at the accepted revision.
- Candidate authoritative-file presence check: empty.

## 14. Changed files and working-tree policy

Committed changes since the administrative starting HEAD are confined to the
approved discrepancy resolution, Slice D preappend docs/assertions, the public
minter, its system-identity documentation/exports, and minter tests. The exact
committed path list is:

```text
CLAUDE.md
backend/behavior_evaluation/README.md
backend/model_kernel/README.md
backend/system_identity/README.md
backend/system_identity/__init__.py
backend/system_identity/minting.py
docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md
docs/superpowers/plans/2026-08-29-bh001-adversarial-acceptance-matrix.md
docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-acceptance-matrix.md
docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-rehearsal-plan.md
docs/superpowers/reports/2026-08-30-bh001-slice-d-preappend-rehearsal-report.md
docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md
tests/identity_binding/test_behavior_anchor.py
tests/identity_binding/test_port_anchor.py
tests/identity_binding/test_variable_anchor_minter.py
tests/model_kernel/test_behavior_slice_d_rehearsal_documentation.py
```

The owner-gate artifacts intentionally remain uncommitted under the file-first
protocol:

```text
docs/superpowers/reports/2026-08-30-bh001-slice-d-candidate-identities.json
docs/superpowers/reports/2026-08-30-bh001-slice-d-preappend-rehearsal-results.md
tests/model_kernel/bh001_slice_d_rehearsal.py
tests/model_kernel/test_bh001_slice_d_preappend_rehearsal.py
```

No model, binding, interpretation, temporal, source, raw, structural, PT, or
VP fixture path is modified. No artifact-generation production logic changed.

## 15. Disclaimer, exclusions, and owner decision requested

> This is an illustrative synthetic BH-001 exact-numeric-equality declaration.
> It does not describe or claim any real printer physics, target, command,
> response, control loop, wiring, signal path, flow, causality, simultaneity,
> correctness, safety, health, real-machine behavior, or operating condition.
> Shared ownership, names, topology, VPA associations, semantic compatibility,
> constraints, and observed correlation did not create this declaration.

The `not_executed` result is an honest admission result, not evidence that the
declared relation is false.

This gate does not add a VSP, VSM, entity, port, VPA, constraint, binding,
interpretation, temporal/source record, BHW, correction, fork, second root, or
executable equality result. It does not claim target, command, sensor,
actuator, flow, direction, influence, causality, control, health, safety,
diagnosis, recommendation, or real-machine operation. Shared ownership did
not create or corroborate the behavior.

`equal` and `different` remain confined to disposable Slice C test worlds.
The candidate committed demonstration remains deliberately declaration-only
and honestly unevaluable.

The genuine remaining owner question is whether to approve the exact frozen
candidate anchors, three canonical records and hashes, 32-record membership,
candidate revision, and 122,406-byte artifact contract listed in this report.
Until that approval, no authoritative append is permitted.

## 16. Final verification status

The final complete repository command over `tests/` completed green on the
current rehearsal files:

```text
2780 passed in 691.55s (0:11:31)
```

Final checks:

- Focused rehearsal gate, independently rerun by the test specialist on the
  final files: `13 passed in 63.91s`.
- Affected BH/kernel/state group: `344 passed in 175.53s`.
- Public minter/documentation group: `71 passed in 1.93s`.
- `git diff --check`: pass.
- Untracked-file whitespace checks: pass.
- Rehearsal helper compilation: pass.
- Branch: `bh001`.
- Committed HEAD:
  `2bee0f3808335d57d5d835f66892d1c21004d519`.
- No configured branch upstream and no push or merge performed.
- Working tree contains only the four uncommitted owner-gate artifacts listed
  in Section 14.

Clean-checkout reproduction of these exact owner-gate files is intentionally
deferred because the file-first protocol keeps them uncommitted until the
owner approves the candidate contract. This rehearsal instead proves
independence using two fresh ledger roots, two separate hash-seed processes,
reversed predecessor copy order, and complete protected-tree inventories.
After owner approval makes the contract commit-authoritative, Slice D final
verification must reproduce it in the required clean checkouts.

END OF BH-001 SLICE D PRE-APPEND REHEARSAL RESULTS
