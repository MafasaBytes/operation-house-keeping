# SN-001 owner follow-up repair — red-baseline evidence (2026-08-12)

The owner's independent verification of the audit repair at `7eaff7f`
confirmed the fast-forward topology, the untouched ledgers, and the
independent all-extras result (1412 passed / 0 failed / 0 skipped), and
reproduced two further contract defects. Each reproduction is encoded in

```
tests/model_kernel/test_structural_evidence_arm.py
    (TestKR6CanonicalStepPathEncoding — reproduction 1, kernel half)
tests/structural_evidence/test_owner_followup_repairs.py
    (TestF2DerivedPathStepsEvidenceBacked — reproduction 2;
     TestF1ForgedNoncanonicalCitationsStayTyped — retained twins)
```

Observed by running exactly those tests against the UNMODIFIED `7eaff7f`
tree (all-extras venv):

```
11 failed, 12 passed
```

The 12 passes are deliberate valid twins and already-holding behavior,
each marked in its docstring: the six canonical-encoding twins (raw
unreserved text, encoded reserved characters, valid UTF-8, the literal
percent, the canonically double-encoded string "%41", and a canonical
usage value), the four-arms/root-sentinel guard, the two valid
derived-path twins (direct-root usage; coherent two-level chain), the
ambiguity-gates-steps rule, and the two forged-citation inversions that
`from_kernel_evidence`'s canonical re-encoding guard already refuses
with typed `SN_LOCATOR_VALUE_INVALID`.

## The 11 failures, mapped to the owner reproductions

Reproduction 1 — noncanonical STEP path encodings construct in the
kernel arm (7):

```
TestKR6CanonicalStepPathEncoding::test_a_noncanonical_encoding_is_unconstructible
  p=%41;d=<32hex>                       over-encoded unreserved 'A'
                                        (the owner reproduction)
  p=%FF;d=<32hex>                       invalid UTF-8
                                        (the owner reproduction)
  p=%C3;d=<32hex>                       truncated UTF-8 sequence
  p=0%3A1%41;d=<32hex>                  embedded over-encoding
  p=%41;i=<32hex>;dp=0%3A1;pp=          usage `p` component
  p=0%3A1;i=<32hex>;dp=%FF;pp=          usage `dp` component
  p=0%3A1;i=<32hex>;dp=0%3A1%3A1;pp=%41 usage non-empty `pp` component
```

Reproduction 2 — unique derived-path steps are not evidence-backed (4):

```
TestF2DerivedPathStepsEvidenceBacked::
  test_the_owner_reproduction_is_unconstructible
      a unique path whose steps contain an arbitrary StepUsageLocator
      absent from the claim set CONSTRUCTED at 7eaff7f
  test_a_unique_path_ends_at_its_for_usage
  test_adjacent_steps_must_chain_parent_to_child
  test_repeated_steps_are_rejected
```

No production change in this commit; the tests land with their fixes so
every commit stays green.
