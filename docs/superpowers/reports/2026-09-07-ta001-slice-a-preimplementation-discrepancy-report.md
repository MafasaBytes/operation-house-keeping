# TA-001 Slice A Preimplementation Discrepancy Report

Date: 2026-09-07

Status: implementation stopped before production or test changes; owner
resolution required

## 1. Outcome

TA-001 Slice A cannot be implemented strictly from the accepted synthesis and
the accepted lower public contracts. Two independently reviewed discrepancies
remain between the frozen TA contract and valid carried lower results:

1. every evidence-bearing state classification carries finite Python `float`
   disclosures, while TA forbids every float during preflight and canonical
   encoding and permits no corresponding normalization; and
2. acceptance row T43 requires a structured result for an alternate governing
   candidate that cannot exist in a valid state-classification condition.

The first discrepancy blocks every evidence-bearing positive or negative TA
execution world. The second makes one accepted public acceptance row
unreachable without forging a lower result that its own nominal validator
rejects.

The implementation prompt requires a stop in either condition. No
`backend/transition_assessment` package, production change, behavioral test,
fixture, demonstration, ledger append, or Slice B work has been created.

## 2. Verified checkpoint and completed administrative work

The verified starting checkpoint was branch `ta001` at:

`a4754d8659c08af8fb86bf18bd3c5aac4ea355fe`

The accepted synthesis remained exact at SHA-256:

`99db3b31f5fa94eb119b32529784a64aff08c604f71ee9eb7530225963816062`

The frozen proposal, challenger audit, and reconciliation report remained at
their accepted SHA-256 values:

| Record | SHA-256 |
|---|---|
| TA-001 proposal | `a8130d3146af7c159d739b6c63b9e0c398fd0bf4f1fa363d99559c476a0cf146` |
| Challenger audit | `b87d607d7ab17bf59bff10678175443303dc81c41726923f40d29034032fdad1` |
| Documentation reconciliation report | `491edeba12197c1ec94e8624720467f0a5ce85e87e03a15f182d0309cd8f9fd4` |

The prompt-required administrative and planning gates were completed before
the lower-contract contradiction was exposed:

- `4d9424f0779a67cdf0c756f3f231d8821d33e83b` —
  `docs: authorize TA-001 Slice A`;
- `78eee5e15b0a36b117d9f7f45e9abbe455d5f868` —
  `docs: plan TA-001 Slice A`.

The administrative documentation/status gate passed 26 tests. Both commits
are documentation only. The implementation plan preserves the contract stop
condition and remains a future executable plan after owner resolution.

## 3. Accepted TA float prohibition

The accepted synthesis requires all of these facts together:

- one request carries both complete `StateClassificationResult` objects;
- one result carries that complete request;
- preflight traverses the complete supplied graph and enforces strict scalar
  kinds before lower validation;
- canonical TA bytes encode the reconstructed result's complete JSON-mode
  field graph;
- serialized shape before and after reconstruction may change only for the
  documented UTC normalization; and
- "Floats and non-finite numbers are forbidden."

The synthesis defines no deterministic normalization of a carried lower float
to an integer, decimal string, or other scalar. Such a conversion would also
change the accepted nominal lower content rather than reconstruct it through
its exact public model.

## 4. Accepted lower float contract

The public TS-001 query result `LatestObservedState` defines:

```python
staleness_seconds: float
```

The production temporal query derives it with:

```python
(as_of - occurrence.received_at).total_seconds()
```

Python `timedelta.total_seconds()` returns a `float`, including when the
mathematical value is integral. An evidence-bearing model-state candidate
carries that complete `LatestObservedState`; the value-compatibility,
semantic-compatibility, constraint-evaluation, and state-classification
results retain it. TA is required to carry the complete classification rather
than replacing or projecting that nested value.

This lower field is an accepted disclosure. Changing its type or its lower
serialization would be a lower-contract change outside the authorized TA
Slice A scope.

## 5. Executable reproduction

A disposable state-classification world was constructed through the current
public orchestration using the existing accepted builders. The resulting
classification was valid and executed. Iterative traversal of its ordinary
Python dump found the following:

```text
classification_execution=executed
float_occurrences=6
first_float_values=[1794.0, 1794.0, 1794.0, 1794.0, 1794.0, 1794.0]
staleness_seconds_runtime_type=float
```

The duplication is expected in the accepted carried lower graph. One finite
float is enough to trigger the TA prohibition. A fully admitted T01 request
must contain governing observed conditions, so it cannot avoid the field by
using an observation-absent lower arm.

Therefore the accepted preflight would classify every executable request as
malformed before its lower results can be reconstructed. Permitting finite
floats privately only during canonical encoding would contradict both the
strict-scalar preflight rule and the explicit canonical prohibition.

## 6. T43 reachability discrepancy

Acceptance row T43 starts from T01, changes the alignment so it "identifies
another candidate," and requires a structured failed gate despite another
aligned occurrence.

Valid lower public results cannot express that world:

1. state classification requires every registered explicit condition's
   evidence-state candidates and semantic candidates to each have length one;
2. constraint evaluation requires one candidate per semantic candidate and
   requires each `semantic_candidate_index` to equal its tuple position;
3. semantic compatibility requires positional parity with the exact carried
   value-compatibility candidates; and
4. evidence alignment derives `aligned_candidate_index` by enumerating that
   exact compatibility.

Consequently candidate index zero is the only valid governing candidate for a
classification condition. A candidate-one alignment requires a forged or
substituted lower graph and fails nominal lower reconstruction. Under the
accepted structural-admission table, that is a typed malformed-input error,
not the structured non-executed result required by T43.

This is separate from T63. T63 correctly requires authoritative result
reconstruction to reject forged divergence between semantic and value index
domains. It does not supply a valid multi-candidate classification world for
T43.

## 7. Why TA cannot repair either discrepancy internally

TA cannot discard `staleness_seconds`, stringify it, coerce it to an integer,
or omit its enclosing lower subgraph. Each option violates exact nominal
reconstruction, serialized-shape preservation, complete carried material, or
canonical-byte rules. Changing `LatestObservedState` would alter a lower
contract, which the authorization expressly forbids.

TA also cannot create a second valid classification candidate, reinterpret an
index from another domain, or accept a forged evidence-alignment result.
Those approaches would weaken the exact full-object join and lower-result
revalidation gates.

No missing public API or store access is involved. The ordinary join is
otherwise implementable from the accepted public carried fields.

## 8. Bounded resolution choices

Owner resolution is required for both items:

1. Pin the treatment of finite floats already carried by accepted lower
   results. The narrowest apparent design correction is to admit ordinary
   finite floats only where an exact nominal lower contract declares them and
   to define their deterministic canonical JSON encoding, while continuing to
   reject float subclasses and all non-finite values. Alternatively, authorize
   a lower-contract migration away from `float`; that is a materially broader
   change.
2. Correct T43 to the malformed-input outcome enforced by current lower
   contracts, or replace it with a reachable candidate-index attack. It must
   not continue to require a structured result from a lower-invalid graph.

Any resolution should state whether the accepted synthesis digest and Slice A
plan are to be updated before implementation resumes. No speculative lower
repair is necessary to demonstrate either discrepancy.

## 9. Preservation and current scope

The authoritative model remains 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FRG/FLD/FLW remains `1/1/0`; TRG/TRD/TRW remains `0/0/0`. No accepted
model, evidence, temporal, identity, membership, ledger, fixture, or artifact
content was changed.

The owner-local `.claude/settings.local.json` was not read for content,
modified, staged, or committed. Slice B remains unauthorized. No facade,
demonstration, second consumer, production package, or lower-layer change was
created. Nothing was pushed, merged, rebased, reset, amended, cherry-picked,
or rewritten.

END OF TA-001 SLICE A PREIMPLEMENTATION DISCREPANCY REPORT
