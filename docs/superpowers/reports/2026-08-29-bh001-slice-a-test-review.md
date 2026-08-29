# BH-001 Slice A independent test and adversarial review

Date: 2026-08-29
Branch: `bh001`
Accepted base: `46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6`
Reviewed implementation commits: `20bd22411a07c9fc2820b5cc15a1ce63df80fd7d`,
`1fb10097c2d0a97ecc007cef4034028c9a5668a2`
Review role: software test engineer
Review scope: BH-001 Slice A only

## 1. Outcome

The committed Slice A implementation correctly establishes the accepted
behavior identity and record foundation, but the first independent review
reproduced one real deterministic-index defect that the original focused suite
did not expose. It also exposed one affected legacy documentation-test
regression after the Slice A status wording was added.

Both failures have been repaired in commit `1fb1009`. The same commit also
closes the two discrepancies identified by the independent backend review: it
adds the exact private effective-body projection and restores all pre-BH
validation ahead of BH admission. The focused suite now reports `110 passed`,
and the complete model-kernel plus affected behavior-anchor suite reports
`1065 passed`.

No remaining production-contract defect was reproduced after those repairs.
The retained tests pin the mixed-invalid validation precedence, the exact
effective-body field set, and input-order independence for every one of the
twelve BH mappings. Independent reruns under three fixed hash seeds were also
green. Two defense-in-depth test-strengthening opportunities remain, recorded
in Section 9; neither is a failed acceptance criterion or a blocker.

Nothing in this review authorizes Slice B queries, Slice C evaluation, Slice D
fixtures, or a change to the accepted architecture.

## 2. Authority and inspected material

The review used:

- the complete corrected BH-001 synthesis;
- the Slice A implementation plan;
- the Slice A adversarial acceptance matrix;
- ADR-0015;
- the complete system-identity and model-kernel Slice A changes in commits
  `19fdca6`, `20bd224`, and repair commit `1fb1009`;
- existing anchor, canonicalization, record-union, store, replay, hostile
  reconstruction, PT, VP, and public-export tests;
- the concurrent backend review report, considered only after this review's
  independent reproduction had been obtained.

The authoritative specification requires all twelve BH `LoadedModel` indexes
to be defensive immutable mappings, with deterministic mapping-key iteration
and deterministic tuple values. It also requires stable collection validation:
all accepted pre-BH paths are validated before the additive BH path.

No implementation, fixture, ledger, binding, temporal, source, interpretation,
or artifact file was modified by this test review. Only this report was added.

## 3. Initial focused verification

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/identity_binding/test_behavior_anchor.py \
  tests/model_kernel/test_behavior_records.py \
  tests/model_kernel/test_behavior_canonical.py \
  tests/model_kernel/test_behavior_store.py \
  tests/model_kernel/test_behavior_revalidation.py -q
```

Result against committed implementation `20bd224`:

```text
107 passed in 20.01s
```

That green result covered all existing focused tests but did not prove that
multi-record mapping iteration was independent of caller input order. The
existing hash-seed reproduction used only one BRG and one BHW, and omitted two
of the affected lifecycle mappings from its serialized projection.

## 4. Finding BHT-A-01 — four BH mappings preserved caller insertion order

Severity: high against the accepted deterministic public index contract.
Initial result: reproduced.
Current result: repaired and fixed-after verified.

The committed implementation froze four mappings without first rebuilding
their keys in canonical order:

- `behavior_registrations`;
- `behavior_rule_superseded_by`;
- `behavior_rule_withdrawals`;
- `behavior_rule_withdrawn_by`.

Immutability was intact, but iteration order depended on the insertion order
of the caller-supplied record mapping. The same model membership therefore
produced observably different public index iteration.

### 4.1 Minimal reproduction

The reproduction built two behavior registrations, two declaration lineages,
and two withdrawals through the public builders. It called
`validate_record_collection()` over:

```text
{record.record_id: record for record in records}
```

and then over:

```text
{record.record_id: record for record in reversed(records)}
```

Before repair, comparison of `tuple(mapping)` produced:

```text
behavior_registrations:           False
behavior_rule_superseded_by:      False
behavior_rule_withdrawals:        False
behavior_rule_withdrawn_by:       False
```

The other eight required BH mapping key orders were equal.

### 4.2 Repair review

The repair reconstructs each affected mapping by sorted record ID immediately
before creating its defensive immutable copy. A retained multi-registration,
multi-lineage, multi-withdrawal regression now checks key order for all twelve
BH mappings under forward and reverse input.

Fixed-after manual reproduction:

```text
all twelve BH mapping key orders equal: True
```

The repair changes no record content, canonical ID, revision membership, or
pre-BH index.

## 5. Finding BHT-A-02 — BH status wording escaped the PT status boundary

Severity: medium integration-test regression; no model semantic defect.
Initial result: reproduced.
Current result: repaired and fixed-after verified.

The first affected model-kernel run reported:

```text
1 failed, 1061 passed in 97.06s
```

The failure was:

```text
tests/model_kernel/test_demo_pt001.py::
test_pt001_final_owner_acceptance_status_is_exact
```

The legacy test isolated its PT status tail using older intermediate VP status
sentences. The repository now carries the final accepted VP sentence,
`VP-001 complete, owner accepted, ...`, so newly added and correct BH wording
containing `awaiting owner acceptance` remained inside the test's PT substring
and was incorrectly attributed to PT.

The bounded repair adds the accepted final VP status prefix as the first
boundary recognized by the legacy test. It does not weaken the PT status
assertions and does not change any runtime behavior.

Fixed-after command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_demo_pt001.py::\
test_pt001_final_owner_acceptance_status_is_exact -q
```

Result:

```text
1 passed in 1.65s
```

## 6. Concurrent backend findings independently checked

The backend review identified two additional committed-source discrepancies.
This test review inspected their repairs and independently exercised their
observable behavior.

### 6.1 Effective engineering body

Slice A now supplies one private, unpersisted canonical helper whose projection
contains exactly:

```text
behavior_anchor_id
context
participant_semantics
rule
evaluation_basis
```

The helper is not exported and does not create an ID, digest, query result, or
stored value. Manual adversarial checks confirmed:

```text
evidence/authority/time/note/parent/id/order variants equal: True
context or keyed-lock variants different:                    True
```

This is the correct foundation for Slice B body grouping. No body group,
corroboration conclusion, or winner is implemented in Slice A.

### 6.2 Stable validation precedence

BH semantic/store validation now runs after the unchanged pre-BH validation
paths, while still using the already-derived entity and variable registration
indexes.

A manual mixed-invalid reproduction contained both:

- a cross-variable VSP correction, which is an invalid pre-BH lineage; and
- a cross-context BHD correction, which is an invalid BH lineage.

The current validator returned:

```text
MODEL_SPECIFICATION_LINEAGE_INVALID
```

This confirms the accepted pre-BH-before-BH failure precedence.

The same mixed-invalid case is now retained as
`TestBehaviorRegistrationAdmission::`
`test_all_pre_bh_validation_precedes_behavior_admission`, so this is no longer
only a manual observation.

## 7. Current focused and affected verification

### 7.1 Focused Slice A suite

The command from Section 3 was rerun after repair.

```text
110 passed in 14.41s
```

### 7.2 Complete model-kernel plus behavior-anchor suite

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/model_kernel tests/identity_binding/test_behavior_anchor.py -q
```

Result:

```text
1065 passed in 73.98s
```

### 7.3 Preservation demonstrated by the focused suite

The focused tests also verified:

- explicit 9-, 10-, 11-, 14-, 16-, 18-, 28-, and 29-record replay;
- unchanged historical revision IDs;
- all twelve BH indexes empty and immutable in pre-BH memberships;
- exactly 29 committed demo records and no BRG, BHD, or BHW fixture;
- every accepted model-record byte unchanged;
- unchanged PT and VP deterministic artifact bytes and SHA-256 values;
- no Slice B query method or result;
- no `backend/behavior_evaluation` package;
- no kernel upward import;
- no port, VPA, state, observation-selection, or numeric-comparison field.

## 8. Contract and adversarial coverage assessment

The current suite materially covers:

- exact opaque `bhv_` identity, UUID4 minting, frozen/extra-forbidden shape,
  and hostile instance revalidation;
- exact BRG/BHD/BHW fields, literals, prefixes, evidence citation arms, and
  public exports;
- the two distinct unordered variable pair and variable-keyed semantic locks;
- exact quantity-kind and unit equality with differing observation roles;
- role, direction, expression, coefficient, tolerance, port, VPA, outcome,
  safety, control, and state exclusions;
- exact golden canonical bytes and IDs;
- parent/evidence/participant input canonicalization;
- stale IDs, discriminator attacks, malformed filenames, hostile nested
  objects, atomic append, and on-disk reconstruction;
- VRG and owner closure, exact citations, owner declarations, additional
  evidence closure, cross-owner admission, and permanent registration;
- context-separated roots, chains, same-root forks, partial/full convergence,
  independent roots, cross-root rejection, and crafted cycles;
- current-tip withdrawal, duplicate/non-tip/unknown rejection, complete
  inactivity, timestamp non-ranking, and historical revival;
- immutable indexes, current multi-record key-order determinism, hash-seed
  stability for the original projection, explicit replay, artifact freeze, and
  import isolation.

No test or implementation path infers behavior from names, common ownership,
hierarchy, ports, VPA, PIF, PCN, PCM, semantics, constraints, observations, or
temporal correlation.

## 9. Defense-in-depth coverage opportunities

These are non-blocking test-maintenance recommendations, not missing accepted
behavior and not reproduced production failures.

### 9.1 Additional effective-body value twins

The retained test pins the exact five-field projection, proves that note and
recorded-time changes are excluded, and proves that a keyed-lock change is
included. Because the exact key set is asserted, evidence, authority,
supersedes, note, time, and record ID cannot enter the projection unnoticed.

For easier future diagnosis during Slice B, individual value twins could also
pin behavior-anchor and context changes and separately vary every excluded
audit/provenance field. This would improve failure localization without
changing the current contract coverage.

### 9.2 One combined all-mapping value projection

The retained multi-record regression compares key iteration for all twelve
mappings under forward and reverse input. The subprocess regression compares
normalized key/value projections and exact stdout under three inner hash
seeds. This review additionally reran both tests under outer hash seeds `1`,
`17`, and `31337`; all six invocations passed.

As future defense in depth, the subprocess projection could include the three
currently omitted mappings and use the multi-registration fixture. The
present combination already detects the reproduced defect, pins all twelve
mapping key orders, and tests tuple contents throughout the focused lifecycle
suite.

## 10. Final review verdict

The initial committed implementation was not adversarially complete because
four public mappings violated the accepted deterministic-iteration contract.
The current repair fixes that defect without changing canonical records or
scope. The documentation boundary regression is also fixed, and both focused
and affected suites are green.

The current Slice A production behavior and retained test evidence are
consistent with the corrected owner-accepted architecture. No blocking test
or adversarial finding remains. Section 9 records only optional future
failure-localization improvements.

Slices B, C, and D remain unstarted. The committed demo remains unchanged.

END OF BH-001 SLICE A TEST REVIEW
