# ES-001 Group-2 failing-before integrity evidence (2026-08-13)

Observed against the unmodified tree at `25b7da6` (docs-only on top of
`8cb5f1e`). Both defects are repaired in Group 3; no production change
in this commit.

## 1. The accepted byte-freeze maps are incomplete

`tests/model_kernel/test_demo_model.py` pins 11 of 14 committed model
records (`FROZEN_MK001_RECORDS` 9 + `FROZEN_VS001_RECORD` 1 +
`FROZEN_VM001_RECORD` 1) and 7 of 11 committed binding records
(`FROZEN_PRE_SN001_BINDING_RECORDS`). The three SN-001 model records and
four SN-001 binding records are authority-checked but NOT hash-pinned,
so a mutation of those bytes would not be mechanically detected. Their
digests, measured now and added to the freeze maps in Group 3 (before
any ES-001 append):

```
models/demo-printer/records/
  reg_c17de916b41ab5f6bcdf4165f47da1d604689e1eafa9afc31ea99092eacbcc90.json
    6c572dd6d1af044bb3bc45937bdedfc5b1308a926684b19ece0145bd80587dd8
  rel_2978509392132152b2d74beb139d2f85e8508f6c50e6ebfea996cd7c78fcf0d5.json
    53242190bb0d3bc840aeb6507207c7ab586a277ee2a88f4fc750bb3493dec7fe
  rtd_04b8da45255190340e7366ce2a373a9b402dc32eb86b6312f382f5e37a4e81b7.json
    b57a7afda3627f1e7ebcfc82c7baecc951610a7e0379642c63ce403e39c123e0

bindings/demo-printer/records/
  iba_2061f4017a7f2355a36d30ee69a6ebc24a94de2e1db8866b4216916678b4d5aa.json
    2eec748ec43373b1c0bd5aa2744466f94db9c0f0d19503754077b6277c3d7a82
  iba_22a8eef16595ec5d38f9135b04499c76f358055a6e5ea4dba9c62f7d9b9d3a43.json
    df6c955a834121493966b509a4c67da73d22bcee2a4271b62976bfa90256e615

bindings/demo-printer-model/records/
  anc_4a576f8b7630176969e2c3186ae5c8233e71311cfbac7c071d7c125b32e0bfdb.json
    972a8407582523836250898f0961e7dc412e9e0e07d3d3a9375aee5f7d1799b1
  iba_162f634fe39b38369db141c76718140340773f0080bca628503090eac445fa08.json
    e782c90f413dc9de49a9242be97580e834fc1fc1ed2824457dddaacad3d281b1
```

## 2. A `vsp_` citing absent model-record evidence loads (EC1)

`validate_record_collection` checks `ModelRecordEvidence.record_id`
membership only for relationship assertions
(`backend/model_kernel/store.py:343-348`); the `vsp` validation pass
(`store.py:197-260`) never reads `record.evidence`. Reproduction, run
against the unmodified tree: a three-record collection
(entity registration + variable registration + a
`VariableValueSpecification` whose evidence is exactly one
`ModelRecordEvidence` citing `vrg_ffffffff…` — absent from the
collection), built through the accepted `build_record` and validated
through the public `validate_record_collection`:

```
LOADED OK — revision mrv_3d0575de97106883 record_count 3
the vsp cites ABSENT vrg_ffffffff...: NO ERROR RAISED (the defect)
```

Expected after the Group-3 repair: the same collection fails typed
`MODEL_REFERENCE_INVALID` at load, prospective append, and explicit
replay subsets — the uniform rule for every evidence-bearing model claim
(`rel_`, `vsp_`, and the forthcoming `vsm_`). The committed ledgers are
unaffected: no committed record cites a model record absent from its
revision (verified by the Group-3 committed-ledger regression).
