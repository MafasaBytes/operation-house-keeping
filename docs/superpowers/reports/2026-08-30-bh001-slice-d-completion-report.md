# BH-001 Slice D Completion Report

Status: BH-001 Slices A, B, and C are owner accepted. Slice D is implemented,
adversarially reviewed, and dual-clean-checkout verified. Final BH-001 owner
acceptance remains pending.

This report records the bounded authoritative demonstration append and final
verification authorized by the owner. It does not declare final owner
acceptance, push or merge the branch, or authorize another BH-001 change.

## 1. Repository boundary and outcome

| Item | Verified value |
|---|---|
| Branch | `bh001` |
| Owner-approved starting HEAD | `2bee0f3808335d57d5d835f66892d1c21004d519` |
| Accepted upstream baseline | `main` and `origin/main` at `46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6` |
| Final implementation HEAD | `6fdf4d009538ddd169c1342508a104c9d61560b6` |
| Branch topology | zero behind and 35 commits ahead of `origin/main` |
| Authoritative record count | exactly 32 |
| Pre-BH membership | exactly 29 explicit record IDs |
| Final revision | `mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b` |
| Push or merge | none |

The authoritative ledger gained exactly three files: one
`VariableRegistration`, one `BehaviorRegistration`, and one parentless
`BehaviorRuleDeclaration`. No other ledger, fixture, source, binding,
interpretation, temporal evidence, identity, or artifact file changed.

## 2. Owner-gate inputs and immutable allocation

The approved gate inputs were read and verified before the append:

| Artifact | SHA-256 |
|---|---|
| `docs/superpowers/reports/2026-08-30-bh001-slice-d-preappend-rehearsal-results.md` | `0a559255359440f54f370eaf11645122089d4c0744e537c9446e20c12ffd4778` |
| `docs/superpowers/reports/2026-08-30-bh001-slice-d-candidate-identities.json` | `8524e9219ee7e1e452d7390f00df99c790bc8d91068e04fc4ec4f7463f75ea07` |

The allocation manifest was not rewritten. Its
`status: "non_authoritative_candidate"` describes the allocation state when
the file was created; the later owner decision approved those exact inputs.
No minter was called during the append or final verification.

Approved anchors:

- variable: `var_ab2d312466054c20b0ac764e9bc0114e`;
- behavior: `bhv_80e21f1682e449ca9c65a5e2ee051ea0`.

The variable remains neutrally named `Synthetic comparison variable`. The
behavior remains `Synthetic exact numeric equality`. Neither name creates or
strengthens the behavior claim.

## 3. Commits

Exactly three commits follow the owner-approved starting HEAD:

```text
0905de0 test: pin BH-001 Slice D preappend contract
13e3c1f docs: approve BH-001 Slice D append contract
6fdf4d0 feat: add BH-001 synthetic demonstration
```

The first commit records the frozen manifest, rehearsal results, helper, and
rehearsal tests. The second separately records the owner approval. The third
contains the authoritative append, explicit replay boundary, deterministic
generator contract, fixture/adversarial tests, and living documentation.

No commit was amended and no rebase, reset, cherry-pick, merge, push, or
history rewrite was performed.

## 4. Authoritative append evidence

Before touching the authoritative ledger, a clean detached checkout at
`13e3c1f` reproduced the owner-approved candidate contract:

```text
20 passed in 43.72s
```

The append driver reconstructed the frozen anchors through their public
contracts, called the public `build_record()` path exposed by
`candidate_records()`, then executed this public store sequence:

```python
store = ModelStore(Path("models/demo-printer"))
for record in (variable_registration,
               behavior_registration,
               behavior_rule_declaration):
    store.append(record)
```

The physical sequence was exactly VRG, then BRG, then BHD. After each append,
the new stored file was read immediately and its ID, byte count, and SHA-256
were compared with the owner-approved golden before the next append.

| Record | Record ID | Bytes | Stored-file SHA-256 |
|---|---|---:|---|
| VariableRegistration | `vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6` | 630 | `0652fd7ca32de43d3e21c5a41a5117eb3c19d2a469ffa30f37b407f91937e285` |
| BehaviorRegistration | `brg_1fd13b69377257d987775c56f7abf9eedd466d4ca6555ff33ba6b8cf6e815d5e` | 1,376 | `19068707d3bb5423eab4db189208d85749ef18cc3447135d8cfa4ea7f0e89edb` |
| BehaviorRuleDeclaration | `bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e` | 2,333 | `fa1a40272d100eb81cc15e64cff782a654b3369a91da62bc36b1f26a2cf655cf` |

The stored bytes equal the independently rehearsed public-builder bytes. The
complete canonical contents remain in the immutable approved rehearsal report
and are pinned again by `tests/model_kernel/test_demo_bh001.py`.

## 5. Exact record semantics

The VRG embeds only the approved neutral `VariableAnchor`, existing owner
`ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`, fixture authority, fixed timestamp,
and approved note. It adds no specification, semantics, binding, observation,
port, or operational role.

The BRG permanently registers the unordered, role-free pair:

```text
var_ab2d312466054c20b0ac764e9bc0114e
var_b7e2d3c4f5a6172839405a6b7c8d9e0f
```

under `exact_numeric_equality`. It cites both exact VRGs and the approved
claim-bearing fixture declaration. Shared ownership is not evidence for the
behavior.

The BHD is parentless and declares, only in
`lifecycle_view/as_designed`:

- `rule.kind = exact_numeric_equality`;
- `evaluation_basis = same_acquisition_cohort`;
- equal quantity-kind locks (`temperature`);
- equal unit locks (`degree_celsius`);
- distinct allowed observation-role locks (`synthetic_comparison` and
  `measured_actual`);
- the exact approved evidence, authority, timestamp, and note.

The committed fixture contains zero BHW records, corrections, successors,
forks, convergence records, or second behavior roots.

## 6. Explicit memberships and revisions

The predecessor remains the exact explicit `VP001_MEMBERSHIP` of 29 record
IDs at:

```text
mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652
```

The three-record set difference is exactly:

```text
vrg_399bbea96bc27689ecab5b6162967b7d7320978117bfe7acddeb05c5ab9aeac6
brg_1fd13b69377257d987775c56f7abf9eedd466d4ca6555ff33ba6b8cf6e815d5e
bhd_fd567f57a0ac6a48309b6d04bb4585ed453a143c7789acc18469525f3536be7e
```

The canonical revision membership is lexicographically sorted and is not the
physical append order:

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

That exact membership produces:

```text
mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b
```

Every 9/10/11/14/16/18/28/29 history continues to replay from its explicit
membership. No test or generator reconstructs a historical membership from a
prefix, timestamp, append order, or directory enumeration.

## 7. Kernel query disclosure

The public Slice B queries over the explicit 32-record membership return:

| Query | Result |
|---|---|
| `behavior(bhv_80e21…)` | `registered`; exact BRG; exact unordered pair |
| `behavior_declaration(..., context=as_designed)` | `declared`; `healthy`; `one_healthy_root` |
| current declaration tips | exactly the approved BHD |
| root lineage | root = lineage = current tip = approved BHD |
| successors | empty |
| withdrawals | empty |
| reverse query from candidate variable | `registered`; one declared/healthy entry to the existing variable |
| reverse query from existing variable | `registered`; one declared/healthy entry to the candidate variable |
| BRG assertion | `found`; event fields are not applicable |
| BHD assertion | `found`; `current`; containing lineage `healthy`; no successor or withdrawal |

The explicit 29-record replay returns:

```text
behavior registration:       not_registered
behavior declaration:        not_registered
existing variable reverse:   registered, zero entries
BRG assertion:               not_found
BHD assertion:               not_found
```

No query selects a winner by authority, time, record ID, filename, or append
order. Record IDs provide deterministic display ordering only.

## 8. Evaluator disclosure

The authoritative demonstration composes the public evaluator with two exact
selectors and the accepted lower evidence world. Its outer result is:

```text
execution:          not_executed
computed_relation:  None
cohort_admission:   not_evaluated
```

Candidate participant (`participant_index=0`):

```text
variable_anchor_id:         var_ab2d312466054c20b0ac764e9bc0114e
model_admission:            admitted
observation_availability:   none_before_cutoff
attachment_admission:       not_evaluated
semantic_admission:         not_evaluated
unit_admission:             not_evaluated
lock_admission:             not_evaluated
numeric_admission:          not_evaluated
canonical_decimal:          None
aggregate admission:        not_admitted
refusals, in exact order:
  1. observation_absent
  2. numeric_specification_not_available
  3. model_quantity_kind_not_available
  4. model_observation_role_not_available
```

Existing participant (`participant_index=1`):

```text
variable_anchor_id:         var_b7e2d3c4f5a6172839405a6b7c8d9e0f
observation_availability:   observed
attachment_admission:       attached
semantic_admission:         admitted
unit_admission:             exact
lock_admission:             matched
numeric_admission:          not_evaluated
canonical_decimal:          None
refusals:                   empty
```

The existing participant's evidence remains fully disclosed:

```text
value_json:        60.4
received_at:       2026-08-07T20:00:18+00:00
occurrence_id:     cd2579c5bca1c1f71f0170eaa73c74fb
attempt_id:        971cf9dd7a595e13c5a74ba505ad92be
observation_id:    297be88ea705222d9b03b97733276774
raw_record_id:     698aa72a05a317e62b62274ffcb3bbfb
payload_checksum:  sha256:6771710d0a97db795a53192e1c6d463937deaa8c11e6fce3d35285d69114caf2
```

The nested semantic results equal the direct semantic queries, nested state
results equal direct `variable_state()` calls, and the occurrence equals the
direct temporal query. No missing binding, specification, semantics,
interpretation, occurrence, or value was fabricated. Neither `equal` nor
`different` is produced.

Provenance axes remain separate:

```text
model revision:           mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b
binding revision:         rev_67af9095cb5a75fc9022b7666a9a68d1eed48f03750f8e26759b745240e60b93
interpretation revision:  irv_6b65d609f8074091e1e09aee99c8b4a0360ecacd672ff99ede5a076c2b3cd57f
temporal cutoff:          2026-08-07T20:30:00+00:00
```

No cross-clock synchronization or shared validity interval is claimed.

## 9. Binding-seam proof

The approved candidate variable is the sole exact registered-anchor exception
without a committed binding `AnchorDeclaration`.

Verified facts:

- all six pre-existing declared anchors remain field-for-field exact;
- the candidate variable is absent from both binding ledgers;
- model state reports `binding_declaration_absent`;
- a second undeclared variable fails the fixture/artifact seam;
- a divergent candidate anchor or VRG fails;
- stale-ID `model_copy` and `model_construct` twins fail;
- omission of each one of the six pre-existing anchors fails independently;
- both binding ledgers, their revisions, file counts, and bytes are unchanged.

The adversarial reviewer found that the first seam helper checked the supplied
records but did not prove their completeness. A hostile map containing only
the candidate was initially accepted by that helper. The repair now requires
the observed pre-existing key set to equal the exact committed declaration set,
and six omission attacks pin the boundary.

This is a fixture-integrity seam, not a new kernel or binding-store admission
rule. The lower layers continue to disclose the missing binding honestly.

## 10. Byte and artifact preservation

All 29 predecessor files were hashed before and after the append. Their
aggregate remains:

```text
962a4ab5551435d849739bb4cff2e5379be03424265a40d4fe4a4b8c2c7e99cf
```

Every predecessor file remains present and byte-identical. The only new model
files are the approved VRG, BRG, and BHD.

Accepted artifact preservation:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| PT-001 | 33,855 | `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8` |
| VP-001 | 17,824 | `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3` |
| BH-001 owner-approved candidate disclosure | 122,406 | `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3` |

The BH bytes intentionally remain the owner-approved **pre-append candidate
disclosure artifact**. Its embedded `authoritative_append_performed=false` and
`records_proposed` fields describe the frozen rehearsal scope. Reproducing
those bytes after append proves the approved generator contract; those fields
are not presented as current repository state and were not rewritten to
manufacture a different golden.

No committed BH artifact file or persisted evaluation result was introduced.
The deterministic generator contract is the public-API-only rehearsal helper
plus exact fixture tests.

## 11. Disclaimer and limitations

The disclosure carries this exact disclaimer:

> This is an illustrative synthetic BH-001 exact-numeric-equality declaration. It does not describe or claim any real printer physics, target, command, response, control loop, wiring, signal path, flow, causality, simultaneity, correctness, safety, health, real-machine behavior, or operating condition. Shared ownership, names, topology, VPA associations, semantic compatibility, constraints, and observed correlation did not create this declaration.

The `not_executed` result is an honest admission result, not evidence that the
declared relation is false.

Remaining intentional limitations:

- the committed demonstration cannot execute because the new variable has no
  binding, VSP, VSM, interpretation, or observation;
- `equal` and `different` demonstrations remain only in disposable Slice C
  test worlds;
- BH result validation proves internal coherence of carried public results but
  does not independently authenticate lower raw-source content;
- there is no tolerance, conversion, affine rule, causality, direction, flow,
  control, health, safety, diagnosis, recommendation, or real-machine claim;
- final BH-001 owner acceptance is still pending.

## 12. Adversarial findings and repairs

Independent backend, test, and final-integrity reviews challenged the current
implementation. All blocking findings were reproduced and repaired:

1. Five older guards still treated the 29-record VP membership as the current
   ledger. The red reproduction was `5 failed in 4.15s`. They now pin the
   32-record current ledger while preserving explicit 29-record replay.
2. Kernel isolation initially omitted the `brg`, `bhd`, and `bhw` filename
   arms. The exact allowed vocabulary now includes them and still rejects all
   unrelated prefixes.
3. The binding seam initially accepted a truncated pre-existing declaration
   map. Exact-key-set validation and six omission attacks now fail closed.
4. Living documentation initially described the frozen candidate disclosure
   as an unqualified final artifact. It now distinguishes historical artifact
   scope from current repository state.
5. The first complete-suite attempt exposed a stale structural-demo
   expectation that the owner had only one model variable: `2790 passed,
   1 failed in 726.17s`. The repaired assertion discloses both model-owned
   variables without turning ownership into a binding claim.

Final independent integrity review:

```text
63 focused tests passed in 79.72s
git diff --check passed
no remaining Slice D implementation, test, architecture, or scope blocker
```

No specialist edited the worktree or invoked a minter.

## 13. Verification results

### Focused and affected worktree verification

| Gate | Result |
|---|---|
| Owner-approved pre-append reproduction | 20 passed |
| Focused append/history/preservation tranche | 197 passed |
| Exact living documentation and fixture contract | 31 passed |
| Complete BH identity/kernel/query/evaluator set | 390 passed |
| Final authoritative Slice D fixture file | 10 passed |
| Import/architecture/isolation set | 51 passed |
| Backend compilation | passed |
| `git diff --check` | passed |

### Complete repository suite

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/ -q

2791 passed in 728.30s (0:12:08)
```

### Fresh base-only checkout

Checkout:

```text
/tmp/bh001-slice-d-base-clean-49AuoK/checkout
HEAD 6fdf4d009538ddd169c1342508a104c9d61560b6
```

Dependencies:

```text
venv/bin/pip install -r requirements.txt -r requirements-dev.txt
```

Sandboxed full-suite result:

```text
2755 passed, 35 skipped, 1 sandbox-denied loopback error in 253.94s
```

The isolated loopback rerun with local-socket permission passed in 0.78s.
Effective result:

```text
2756 passed, 35 skipped
```

### Fresh all-extras checkout

Checkout:

```text
/tmp/bh001-slice-d-extras-clean-Wsqu5v/checkout
HEAD 6fdf4d009538ddd169c1342508a104c9d61560b6
```

Dependencies:

```text
venv/bin/pip install -r requirements.txt -r requirements-dev.txt
venv/bin/pip install --require-hashes \
  -r requirements-cad.txt -r requirements-pdf.txt
```

Sandboxed full-suite result:

```text
2790 passed, 1 sandbox-denied loopback error in 295.04s
```

The isolated loopback rerun with local-socket permission passed in 0.76s.
Effective result:

```text
2791 passed
```

Focused all-extras checks:

```text
OCP/STEP: 31 passed in 28.50s
PDF:      89 passed in 30.49s
```

Both clean checkouts independently reproduced:

```text
record count:                  32
model revision:                mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b
predecessor aggregate:         962a4ab5551435d849739bb4cff2e5379be03424265a40d4fe4a4b8c2c7e99cf
candidate artifact bytes:      122406
candidate artifact SHA-256:    4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3
```

The serialized reproduction summaries were byte-identical across the two
columns. Both detached worktrees were clean at the exact implementation HEAD.

## 14. Changed files

Relative to the owner-approved starting HEAD `2bee0f3`, the three commits
changed only these authorized groups:

- status/design documents: `CLAUDE.md`, the model-kernel, model-state,
  behavior-evaluation and system-identity READMEs, ADR-0015, the BH
  specification, Slice D plan/matrix, global matrix, and model/demo READMEs;
- gate artifacts: the immutable candidate manifest and pre-append rehearsal
  results;
- authoritative ledger: the exact approved VRG, BRG, and BHD JSON files;
- deterministic fixture support:
  `tests/model_kernel/bh001_slice_d_rehearsal.py`, its pre-append test, and
  `tests/model_kernel/test_demo_bh001.py`;
- explicit membership/history and preservation adaptations in model-kernel,
  model-state, observation-compatibility, constraint-evaluation, behavior-
  evaluation, and structural-evidence tests.

No production contract, query facade, evaluator, canonicalizer, store,
identity contract, binding, interpretation, temporal/source evidence, PT/VP
record, or artifact-generation algorithm changed in Slice D.

## 15. Final repository state and stop gate

At final verification before writing this report:

```text
branch:                  bh001
implementation HEAD:     6fdf4d009538ddd169c1342508a104c9d61560b6
main:                    46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6
origin/main:             46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6
origin/main...HEAD:      0 behind / 35 ahead
implementation worktree: clean
remote operations:       none
```

After file-first delivery, this completion report is the sole uncommitted
worktree addition. It is intentionally left for the final owner gate.

BH-001 Slice D is implemented and adversarially reviewed; awaiting final owner
acceptance. No further BH-001 slice or repair has started.

END OF BH-001 SLICE D COMPLETION REPORT
