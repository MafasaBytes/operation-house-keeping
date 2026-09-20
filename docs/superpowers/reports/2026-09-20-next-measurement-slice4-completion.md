# Slice 4 bounded minimax and result completion

## Scope

The approved plan names this slice **Slice 4: bounded minimax and result**. The implementation adds `measurement_ranking.py`, an application-owned prior-free minimax layer consuming only a complete qualified matrix. It preserves all nominated candidates, repeated and empty outcome branches, survivor multiplicity, ties, and separate survivor-multiset equivalence. It adds no cost, prior, prediction discovery, command, retention, replay, physical-acquisition, or backend behavior.

The Slice 3 administrative acceptance HEAD is `687ebc1f70833200e61872e49389831c8258d70e`. The Slice 4 implementation and tested HEAD is `e8efb3952b60b73bed84a527e5c86b6a5626aef7`. Slice 3 implementation remains `835f1cd92638eb43d17836c92f90a710a8b1fb97`; Slice 2 acceptance remains `f4dbeefc216273883037ad24e9dccf5e3f785b44`.

## Red/fixed evidence

The Slice 4 ranking tests passed without an implementation repair. The matrix contract requires a complete qualified candidate status; denied, conflicting, unavailable, or inapplicable candidates withhold the whole nominated set. No candidate is silently removed. Invalid survivor IDs reject rather than fabricate a ranking.

## Verification and semantic coverage

The focused selection passed 24 tests: five Slice 4 ranking tests, four Slice 3 support tests, Slice 2 admission tests, Slice 1 contract/closure tests, and the clean legacy replay regression. Coverage includes:

* one nominated procedure discriminating two hypotheses (`worst=1`, reduction `1`);
* ties preserved across equal worst-case scores;
* equal scores separated from survivor-multiset equivalence;
* empty and repeated branches retained in canonical multiset serialization;
* zero-hypothesis and zero-measurement withholding;
* permutation-invariant hypothesis/candidate ordering; and
* unsupported or withheld candidates causing whole-set withholding.

The deliberately misleading unsupported-exclusion result remains confined to test fixtures; no production bypass exists. Ranking consumes qualified support only, so missing/conflicting/denied/inapplicable material cannot create artificial discrimination. Local attestation remains separate from prediction validity and ranking policy.

## Measurements and preservation

The final focused command completed in approximately 20.3 seconds wall time in the existing environment; this is test-process time, not a capacity claim. No approved limit changed. Existing identity, closure, authority, resource, thermal, governed, replay, package/oracle, backend, ledger, runtime-result, and unrelated artifacts remain preserved.

## Remaining obligations and gate

Slice 4 does not qualify new predictions, adjudicate manual C, publish results, add commands, or execute the full proof. Owner review must accept complete-qualified-input gating, minimax arithmetic, withholding, tie/multiset semantics, and the no-cost/no-prior boundary before Slice 5 is separately authorized. Subsequent slices and the full 142-command proof remain unauthorized.
