# ES-001 Group-9 ledger-append red baseline (2026-08-15)

Observed in a disposable detached full worktree at Group-8 HEAD
`7c2b2b6`; no rehearsal record was copied to or committed from the real
`es001` worktree. Records were constructed only through the public
canonical builders and appended only through `ModelStore.append` and
`InterpretationStore.append`.

## Rehearsed exact evolution

The rehearsal produced the mandated counts:

```text
models/demo-printer                 14 -> 16
interpretations/demo-printer         0 -> 3
bindings/demo-printer                6 -> 6
bindings/demo-printer-model          5 -> 5
committed spj records                0 -> 0
```

Derived model records:

```text
observation_role / measured_actual
  vsm_053882a4714f51a0e9d358b5a8598cfca856482d9af9acd0117313a9ab8d1c40
  file sha256 371527c7bd45c3118043b3da3ab2f17bb34769eacea4dd48e84eb148c71ea33a
quantity_kind / temperature
  vsm_3b4b829006033604f088f2ff0e2727f4b2a1987f7d0edc5be54327562ef8791b
  file sha256 b04377e1a5385a2a301ef288a0a211fcf06602914a36a2da334615915659730f
```

Both target
`var_b7e2d3c4f5a6172839405a6b7c8d9e0f`, carry one model-only
`OwnerDeclarationEvidence`, use the fixed
`2026-08-13T12:00:00Z` time and `es001_demo_fixture` authority, and have
no parent. The resulting current model revision is:

```text
mrv_23631989f98b678aaf1c556c345ac57a320ec266c2f712a40099e8032ca8135b
```

Derived interpretation records, all for the exact accepted Moonraker
temperature subject/property pair and the declared fixture interval
`[2026-08-07T20:00:00Z, 2026-08-07T21:00:00Z)`:

```text
observation_role / measured_actual
  spi_07548575f798119990ac283484f81f183208223abc31f314ae042242b72848cc
  file sha256 935655a321f3f0fceb317e1ce1e8e0c51e0c5a2a2ebe1599395bfc2a53c7b19c
quantity_kind / temperature
  spi_2fef48f888b20a82a9c6f535262112527b194de31f07e02e36a7954a78433b92
  file sha256 1851dadef578f49489d1d2555996b168d383044cff56bf3dc81b8471887b2d48
unit / degree_celsius
  spi_5a4eca7a600e2f682514e574d443b22dd0110337c5097902a0920fb6a930682a
  file sha256 e34c0c7bc0b16af364b1bca3d50130575b2bdd38683c4a6f1566eda7f5c103cd
```

They use the same fixed time and authority, have no parents, and state
that the interpretation is authority knowledge rather than
source-supplied evidence. The initial interpretation revision is:

```text
irv_6b65d609f8074091e1e09aee99c8b4a0360ecacd672ff99ede5a076c2b3cd57f
```

## Complete-suite result

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/
```

Result using the existing project environment from the detached copy:

```text
1671 collected
1656 passed
14 failed
1 setup error
363.39 seconds
```

The setup error is the previously known sandbox restriction, not a
ledger-migration defect:
`tests/data_sources/test_http_api_connector.py::TestRealLoopbackTransport::
test_get_redirect_refusal_and_proxy_isolation` cannot create its loopback
listening socket (`PermissionError: [Errno 1] Operation not permitted`).

All 14 failures are expected stale append-sensitive pins. The new
`source_interpretation` and `semantic_compatibility` suites passed in
full against the rehearsed ledgers.

## Exact failure-to-Group-10 migration map

1. `tests/model_kernel/test_demo_model.py::TestCommittedLedger::
   test_golden_revision_and_membership` — current revision remains pinned
   to the 14-record `mrv_702c840f...`. Group 10 pins the new 16-record
   revision and retains the 14-record revision as an explicit-membership
   historical replay.
2. `tests/model_kernel/test_demo_model.py::TestCommittedLedger::
   test_fixture_authority_never_human_owner` — exhaustive authority/count
   guard remains 14 and classifies every non-SN record as
   `mk001_demo_fixture`. Group 10 adds the two exact `vsm` ids mapped to
   `es001_demo_fixture` and changes only the current count to 16.
3. `tests/model_kernel/test_demo_model.py::TestVs001Fixture::
   test_pre_specification_revision_replays_without_it` — `eleven_ids()`
   subtracts only SN-001 ids, so it wrongly includes both later `vsm`
   records and produces `mrv_e32deaa6...`. Group 10 replaces derived
   prefix/subtraction membership with the retained explicit 10/11-record
   historical id lists.
4. `tests/model_kernel/test_isolation.py::TestUpstreamBoundary::
   test_committed_demo_model_lives_under_models_only` — stale count 14;
   Group 10 extends it to 16 without changing the location assertion.
5. `tests/model_kernel/test_sn001_hierarchy_separation.py::
   TestD6Separation::test_i1c_the_type_name_literal_appears_exactly_once_in_the_ledger`
   — stale count 14; Group 10 extends only the count to 16, preserving the
   exact-once hierarchy assertion.
6. `tests/model_kernel/test_structural_evidence_arm.py::
   TestKR1CommittedLedgerUnchanged::test_all_committed_ids_verify_under_the_six_arm_union`
   — stale record count 14; Group 10 migrates it to 16 and continues to
   verify every id.
7. `tests/model_kernel/test_structural_evidence_arm.py::
   TestKR5SchemeSpecificGrammar::test_the_committed_ledger_satisfies_the_grammar`
   — stale record count 14; Group 10 migrates it to 16 without weakening
   locator grammar checks.
8. `tests/model_state/test_demo_join.py::TestCommittedDemoJoin::
   test_committed_demo_old_revision_is_honest_limbo` — the derived
   subtraction replay retains `vsm` while removing `vrg`, correctly
   failing reference closure. Group 10 uses the explicit nine-record
   pre-variable membership; no prefix filter or kind subtraction remains.
9. `tests/model_state/test_isolation.py::TestLedgerVocabulary::
   test_no_locator_or_value_vocabulary_in_model_ledger` — stale count 14;
   Group 10 migrates the guard to 16 and leaves every vocabulary needle
   intact.
10. `tests/observation_compatibility/test_demo_compatibility.py::
    TestCommittedDemonstration::test_pre_specification_replay_is_attached_but_unspecified`
    — same derived historical-membership defect as item 3. Group 10 uses
    the explicit ten-record pre-specification membership.
11. `tests/observation_compatibility/test_demo_compatibility.py::
    TestCommittedDemonstration::test_no_accepted_record_hash_changed` —
    stale current count 14. Group 10 changes it to 16, verifies every id,
    and extends the byte-freeze map with the two new `vsm` digests without
    altering any of the existing 14 pins.
12. `tests/observation_compatibility/test_isolation.py::
    TestLedgerVocabulary::test_committed_model_ledger_has_no_source_or_value_vocabulary`
    — stale count 14; Group 10 migrates it to 16 with all needles intact.
13. `tests/structural_evidence/test_demonstration.py::
    TestDM1TheCompleteChain::test_the_golden_finding_multiset_and_every_arrow`
    — helper pins the old current revision. Group 10 updates that helper
    to the new 16-record revision while retaining the 14-record replay pin.
14. `tests/structural_evidence/test_demonstration.py::
    TestDM1TheCompleteChain::test_every_subject_is_accounted_for` — same
    shared stale current-revision helper as item 13; the same bounded
    migration repairs it.

Group 10 must additionally add the new interpretation-ledger golden
revision/count/authority/byte pins and the explicit three-id replay test.
Those are new acceptance coverage rather than failures of a pre-existing
pin, so they do not appear among the 14 failures above. Both binding sets
must remain byte- and membership-identical, and no `spj` file may be
committed.

