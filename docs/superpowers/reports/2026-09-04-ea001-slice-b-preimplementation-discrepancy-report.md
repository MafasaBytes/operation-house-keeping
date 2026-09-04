# EA-001 Slice B Preimplementation Discrepancy Report

Date: 2026-09-04

Status: implementation stopped before runtime or test changes; owner resolution required

## 1. Outcome

EA-001 Slice B cannot be implemented strictly from the accepted design and
accepted Slice A implementation without silently weakening the captured-view
protocol or changing Slice A. The owner instruction explicitly requires a
stop and discrepancy report in this condition.

The primary blocker is executable: the accepted source inventory token omits
the possible selected pre-horizon seed and all of its dependencies. A seed
metadata mutation can therefore occur between the initial and final source
fences while both tokens remain exactly equal. The captured seed material
changes, but the required `source_store_changed_during_capture` refusal cannot
be derived from either fence.

A second contract pin is absent: the normative synthesis names three public
result models and refers to supporting limits, issue, and artifact-
revalidation models, but does not specify their fields or field order. It also
does not enumerate the exact package `__all__`. The authorization requires
exact field sets, literal order, and exports, so inventing them would be a
silent public-contract design decision.

No `backend/evidence_assurance` package, Slice B test, runtime change, fixture,
evidence mutation, temporal mutation, model record, ledger change, or Slice C
work has been created.

## 2. Verified authority and administrative gate

The accepted Slice A implementation is:

`873df5bfc4fef2b6c8136612c7a9655048dd6b1b`

The accepted completion report remains exact at:

`4f4786fe214b43370900d44555e42a3603c36fbec009f101e19801c459b4cd03`

The normative synthesis remains exact at:

`a33e8bbea1869889c082ec49f8e9f9966d98f72fc70286f8381f1d7f32db52a0`

The administrative acceptance was completed first in:

`66dd6677cb34c98aad800a06f2f9e01ac60d7a42` — `docs: accept EA-001 Slice A`

That commit adds only the exact accepted completion report and owner-
acceptance record. Before commit, 31 focused documentation/status tests and
the staged whitespace check passed.

The other accepted design records remain:

| Record | SHA-256 |
|---|---|
| Codex lead proposal | `97ddef4ac9a8ee4248fa9d2ffe7e47225172bb741a0a02c5a03f78bee99dbd98` |
| Challenger audit | `14ac3fab976aa007785b2876a035a636306b1ad55ef0a236f12e675977353b81` |
| Final synthesis | `a33e8bbea1869889c082ec49f8e9f9966d98f72fc70286f8381f1d7f32db52a0` |

## 3. Normative seed-fence requirement

The final synthesis requires all of these facts together:

- a selected occurrence may predate the requested horizon;
- the source token binds dependencies for the possible selected pre-horizon
  seed;
- the initial source token is captured before the temporal material read;
- the selected seed attempt ID becomes available only from the temporal
  material;
- source material is then read once using that seed ID;
- final source and temporal tokens fence the same defined fields; and
- a source mutation after the initial token and before source reads, during
  reads, or before the final token refuses under A31–A33.

This is a real content boundary, not merely an optional diagnostic. Section 9
requires refusal when observed membership changes or material disagrees with
its fences.

## 4. Accepted lower source behavior

The accepted public reader signature is:

```python
inventory_token(scope, *, horizon_started_at, as_of)
read_material(
    scope,
    *,
    horizon_started_at,
    as_of,
    selected_seed_attempt_id,
)
```

Only `read_material` accepts the selected seed ID. The accepted filesystem
implementation constructs every inventory token by calling
`read_material(..., selected_seed_attempt_id=None)`. That material retains
only attempts whose effective time is within the declared horizon. It skips
every pre-horizon attempt unless its exact ID is explicitly supplied.

Consequently the source token has no member key for the selected pre-horizon
attempt, its ingestion run, envelope, payload, extraction, or observation.
The final token repeats the same omission.

## 5. Executable reproduction

A disposable DS-004 source and temporal projection were created using the
accepted test builders. One exact observation was projected, and the request
horizon was moved one hour after its receipt so it became the selected
pre-horizon seed with empty attempt-coverage membership.

The reproduction performed this order:

1. capture the accepted source inventory token;
2. read source material with the temporal seed attempt ID;
3. mutate a same-length, valid Date header in that seed attempt metadata;
4. capture the final accepted source inventory token; and
5. reread the same named seed material.

Observed output:

```text
initial_member_count=0
final_member_count=0
tokens_equal=True
seed_descriptor_changed=True
seed_bound_by_token=False
```

The changed metadata is valid and its same-read captured descriptor digest
changes. Source/temporal governed-field parity does not compare this Date
header, so parity cannot substitute for the missing fence. An EA layer using
only the accepted public seam would see equal source fences around different
captured seed content.

This violates the required seed dependency token, Section 9 steps 2, 7, and
8, and A31–A33. It also prevents a complete proof of A36 for crossed changes.

## 6. Why Slice B cannot repair this internally

Slice B cannot know the selected pre-horizon attempt ID until after the
temporal material read in protocol step 4. It is forbidden to read source
material before the initial source fence or to perform an ambient source
reread for derivation. Calling the accepted inventory method with the same
scope and interval after learning the seed still omits that seed.

Changing the request horizon for the token would make it a different token
scope and would incorrectly add pre-horizon attempts to the declared attempt-
coverage interval. Computing a private token from source filesystem paths is
also forbidden by the dependency boundary. Comparing the seed's source fields
only to temporal fields cannot bind source-only metadata bytes or dependency
artifacts.

The defect therefore cannot be repaired inside
`backend.evidence_assurance` while respecting the exact protocol and import
boundary.

## 7. Named-captured-artifact revalidation consequence

The same interface has no exact named-artifact reread operation. The only
material method rereads all currently in-horizon material plus at most one
seed. In `named_captured_artifacts` mode it cannot necessarily reread an old
named artifact that is no longer selected by current horizon membership, and
new in-horizon membership can make the lower read refuse at its global bound
before old named artifacts are checked.

That is narrower than Section 14's requirement to check the exact named
captured artifacts while separately disclosing observed membership relation.
It may yield `refused`, but it cannot guarantee the specified successful
`valid_for_named_captured_artifacts` case for all retained valid snapshots.

## 8. Missing exact public field and export pins

Sections 11.1 and 11.4 pin ordered fields for the request, route, coverage,
selection, fence, assurance, and snapshot. Section 12 pins status and issue
literals. However, the synthesis only references these supporting types
without defining ordered fields:

- `OperationalEvidenceMaterialLimits`;
- `OperationalEvidenceIssue`;
- any per-artifact store-revalidation result;
- `OperationalEvidenceSelectionResult`;
- `OperationalEvidenceStoreRevalidationResult`; and
- `OperationalEvidenceSnapshotValidationResult`.

The text requires offline validation to disclose source-byte and temporal-
store checks as `not_rechecked`, expected-fingerprint relation, computed
fingerprint, and bounded detail, but no exact field names/order are specified.
The two store-bound modes likewise require membership and named-artifact
disclosures without an exact result shape. Section 17 requires exact public
field and `__all__` equality, while no final `__all__` list is present.

The older lead proposal defines different, superseded semantic result shapes
and vocabularies. Renaming or adapting those fields is not a mechanical
operation under the stated authority order.

## 9. Additional query-vocabulary ambiguity

The request has no field that can ask for a cross-clock comparison and the
facade has no alternate comparison method. Nevertheless A21 requires a
"requested comparison" to raise `EA_TIME_COMPARISON_UNSUPPORTED` before I/O.
The exact public trigger for that error is not specified. Adding a request
field would violate the normative request field order; leaving the error
unreachable would leave A21 unimplemented.

This ambiguity is not needed to prove the primary stop, but should be pinned
with the public result shapes before implementation resumes.

## 10. Owner decisions required

1. Authorize one exact lower-seam resolution for selected seed fencing. The
   narrowest apparent option is to require
   `inventory_token(scope, horizon_started_at, as_of)` to discover and bind
   the exact source-side possible selected seed dependencies without changing
   its signature. This changes the accepted Slice A token behavior and its
   deterministic evidence, so it requires explicit owner approval and a new
   accepted digest. An alternate explicit seed-aware token or named-read seam
   would be a larger public-contract change.
2. Pin how `named_captured_artifacts` rereads exact captured logical names when
   they no longer belong to current horizon material or current membership is
   over the normal capture bound.
3. Pin the exact fields and field order of every referenced result/support
   model and the exact package `__all__` list.
4. Pin the public input that requests an unsupported cross-clock comparison,
   or explicitly remove A21 and `EA_TIME_COMPARISON_UNSUPPORTED` from the
   executable Slice B contract.

## 11. Current scope and status

The repository remains at the administrative acceptance plus documentation-
only discrepancy work. No accepted Slice A code or contract was changed. The
accepted lower-material serialization therefore remains untouched. No
production Slice B package exists, no test was added, and no completion report
was written because Slice B is not complete.

Slice C remains unauthorized and unstarted. Nothing was pushed, merged,
rebased, reset, cherry-picked, amended, or rewritten.

END OF EA-001 SLICE B PREIMPLEMENTATION DISCREPANCY REPORT
