# SN-001 owner-audit integrity repair — red-baseline evidence (2026-08-12)

The independent owner audit of branch `sn001` at `81cd0fc` confirmed the
branch topology, the append-only ledger evolution, and the full
all-extras result (1365 passed / 0 failed / 0 skipped), and reproduced
five defects. Each reproduction is encoded as a regression test in

```
tests/structural_evidence/test_owner_audit_repairs.py    (defects 1-5)
tests/model_kernel/test_structural_evidence_arm.py       (defect 4,
                                        TestKR5SchemeSpecificGrammar)
```

Observed by running exactly those two files against the UNMODIFIED
`81cd0fc` tree (all-extras venv):

```
41 failed, 13 passed
```

The 13 passes are the pre-existing arm tests (KR1–KR3, X5) plus the
tests deliberately written as valid twins, stability pins, or
already-holding invariants (each marked in its docstring):
`test_shipped_rules_fingerprints_and_mirrors_are_unchanged`,
`test_wrong_component_count_stays_typed`,
`test_valid_round_trip_twin_for_every_arm`,
`test_namespace_disclosure_kernel_and_digest_material_agree`,
`test_every_arm_constructs_from_its_canonical_grammar`,
`test_the_committed_ledger_satisfies_the_grammar`.

## The 41 failures, mapped to the owner defects

Defect 1 — cross-source relationship-proposal contamination (3):

```
TestD1CrossSourceEndpointContamination::
  test_a_relationship_resolves_exclusively_to_source_a_anchors
      observed at 81cd0fc: the single emitted proposal carried SOURCE
      B's anchors (ENT_PB -> ENT_CB) for source A's containment claim
  test_declared_context_on_b_never_unlocks_a_unknown_containment
      observed: a relationship proposal WAS emitted although source A's
      context is unknown (B's declared context overwrote the
      locator-keyed context map)
  test_two_rules_joining_one_claim_apart_is_not_proposable
      observed: last-rule-wins emitted an edge to the second rule's
      anchor
```

Defect 2 — provenance incoherence constructs (13):

```
TestD2ProvenanceCoherence::  (every test: DID NOT RAISE ValidationError)
  test_the_owner_reproduction_is_unconstructible
      (claim_set.source_ref "declared-source" + claim address
       "foreign-source" constructed successfully)
  test_a_field_from_a_foreign_source_cannot_join_a_claim
  test_bom_row_requires_a_csv_row_locator
  test_bom_row_fields_are_cells_on_the_claims_physical_row
  test_field_name_disclosure_agrees_with_its_cell_locator
  test_step_claim_kinds_require_their_own_locator_schemes
  test_step_fields_address_the_containing_claim_exactly
  test_bom_parent_column_endpoints_are_same_source_row_addresses
  test_step_nauo_usage_edge_endpoint_grammar
  test_containment_endpoints_must_be_disclosed_subject_claims
  test_unresolved_parent_child_belongs_to_the_set_source
  test_derived_path_for_an_undisclosed_usage_is_rejected
  test_disclosure_coverage_compares_exact_addresses
      (a resolved subject at (foreign source, r=1) passed coverage on
       the locator STRING alone)
```

Defect 3 — `applies_to` outside the fingerprint (2):

```
TestD3AppliesToIsABodyDerivedMirror::
  test_widening_applies_to_is_unconstructible
      observed: the widened rule constructed AND kept fingerprint
      57241bb3231eac29 byte-for-byte
  test_substitution_removal_and_reordering_are_rejected
```

Defect 4 — untyped kernel locator values (4 + 17):

```
TestD4TypedConversionErrors::
  test_malformed_integer_is_a_typed_structural_error
      observed: raw ValueError from int("abc") escaped
  test_noncanonical_integer_never_silently_renormalizes
      observed: "r=01" silently reconstructed as r=1
  test_negative_index_is_typed_never_a_pydantic_leak
      observed: raw pydantic ValidationError escaped
  test_malformed_step_identifier_is_typed
      observed: raw pydantic ValidationError escaped
TestKR5SchemeSpecificGrammar::test_a_scheme_value_mismatch_is_unconstructible
  all 17 malformed (scheme, value) pairs CONSTRUCTED at 81cd0fc,
  including the owner reproduction ("csv_row", "r=abc")
```

Defect 5 — duplicated fingerprint implementation, contradictory endpoint
wording (2):

```
TestD5OneToolchainFingerprint::test_the_two_module_names_are_one_function
    observed: rules.toolchain_fingerprint and
    locators.toolchain_fingerprint are two independent function objects
TestD5EndpointGrammarAdjudication::
  test_contract_wording_matches_the_implemented_grammar
    observed: the contract docstring claims "For STEP both endpoints
    are DEFINITIONS" while step_structural_claims emits a usage-address
    child and definition-address parent
```

No production change in this commit; the tests land together with each
defect's repair so that every commit stays green.
