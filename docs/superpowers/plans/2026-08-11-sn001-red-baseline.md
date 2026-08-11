# SN-001c red-baseline evidence (plan commit 10)

Observed by applying the seven authored append records — content-derived
ids computed through the accepted builders, appended through the
validating `BindingStore.append` / `ModelStore.append` — in a **full copy
of the worktree** (post-commit-14 state) and running the complete suite
from that copy's root. The append payloads are reused verbatim at
commits 15–16.

## The seven records

```
iba_S1 -> bindings/demo-printer       iba_2061f4017a7f2355a36d30ee69a6ebc24a94de2e1db8866b4216916678b4d5aa
iba_S2 -> bindings/demo-printer       iba_22a8eef16595ec5d38f9135b04499c76f358055a6e5ea4dba9c62f7d9b9d3a43
anc_S3 -> bindings/demo-printer-model anc_4a576f8b7630176969e2c3186ae5c8233e71311cfbac7c071d7c125b32e0bfdb
iba_S4 -> bindings/demo-printer-model iba_162f634fe39b38369db141c76718140340773f0080bca628503090eac445fa08
rtd_S5 -> models/demo-printer         rtd_04b8da45255190340e7366ce2a373a9b402dc32eb86b6312f382f5e37a4e81b7
reg_S6 -> models/demo-printer         reg_c17de916b41ab5f6bcdf4165f47da1d604689e1eafa9afc31ea99092eacbcc90
rel_S7 -> models/demo-printer         rel_2978509392132152b2d74beb139d2f85e8508f6c50e6ebfea996cd7c78fcf0d5
```

## Observed: 13 failed, 1339 passed

The plan predicted 11 failures against the pre-SN-001 tree plus a 12th
firing at commit 11. Observed against the post-commit-14 tree: the
predicted 11, minus `test_variable_registration` (already migrated at
commit 11), plus three SN-001-era pins that must themselves migrate:

```
tests/identity_binding/test_demo_binding_set.py
  test_loads_valid_with_expected_membership            (:77, 4 -> 6)  -> commit 15
  test_fixture_authority_never_human_owner             (:88, agents)  -> AU1, commit 15
  test_bound_resolution_and_complete_provenance_chain  (:122, 4 -> 6) -> commit 15 (+ RP4)
tests/model_kernel/test_cross_layer_seam.py
  test_every_registration_matches_its_declaration_exactly (:38, 4->5) -> commit 16
tests/model_kernel/test_demo_model.py
  test_golden_revision_and_membership     (load() golden -> RP1)      -> commit 16
  test_fixture_authority_never_human_owner (:43 agents -> AU2)        -> commit 16
  test_pre_specification_revision_replays_without_it (:232 -> RP2)    -> commit 16
tests/model_kernel/test_isolation.py
  test_committed_demo_model_lives_under_models_only (:150/:156)       -> commits 15/16
tests/model_kernel/test_structural_evidence_arm.py
  KR1 test_all_committed_ids_verify_under_the_six_arm_union
      (pins load() at 11 -> migrates to RP1 + CURRENT_REVISION)       -> commit 16
tests/model_state/test_isolation.py
  test_no_locator_or_value_vocabulary_in_model_ledger (:101 count;
      every NEEDLE passes on the three new records)                   -> commit 16 (SV1)
tests/observation_compatibility/test_demo_compatibility.py
  test_no_accepted_record_hash_changed (record_count 11 -> 14)        -> commit 16
tests/observation_compatibility/test_isolation.py
  test_committed_model_ledger_has_no_source_or_value_vocabulary
      (:130 count; needles pass)                                      -> commit 16 (SV1)
tests/structural_evidence/test_reconcile.py
  A12' test_committed_incoherent_fixtures_yield_only_unmapped
      (the committed sets NOW CONTAIN three sx1 mappings citing
       unsupplied showcase sources: the honest multiset gains
       cited_extraction_not_found x3)                                 -> commit 16
```

## The honesty defect, observed live

Both prefix-filter replays **passed silently** in this run while
selecting the wrong membership:

- `tests/model_state/test_demo_join.py:162-164` — selects 12 of 14
  records under a docstring claiming "the committed pre-variable
  revision" (9 records)
- `tests/observation_compatibility/test_demo_compatibility.py:122` —
  selects 13 of 14 under a "pre-specification" (10-record) claim

RP2/HD1 at commit 16 convert both to explicit record-id lists with
revision-id assertions; a prefix filter is never an acceptable
membership selector.
