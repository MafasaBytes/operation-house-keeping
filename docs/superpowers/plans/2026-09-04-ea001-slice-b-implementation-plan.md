# EA-001 Slice B Implementation Plan

Date: 2026-09-04

Status: owner authorized; implementation blocked at the lower-contract gate

Accepted Slice A HEAD: `873df5bfc4fef2b6c8136612c7a9655048dd6b1b`

Slice A acceptance commit: `66dd6677cb34c98aad800a06f2f9e01ac60d7a42`

Normative design:
`docs/superpowers/specs/2026-09-04-ea001-content-bound-operational-evidence-selection-and-assurance-design.md`

Normative design SHA-256:
`a33e8bbea1869889c082ec49f8e9f9966d98f72fc70286f8381f1d7f32db52a0`

## 1. Scope and mandatory stop conditions

Slice B is limited to a read-only `backend.evidence_assurance` composition
package. It may consume only the accepted public DS-004 operational-evidence
reader/contracts, the accepted public temporal query/contracts, Pydantic, and
the standard library. It owns no store, cache, database, ledger, revision,
anchor, minter, persistent receipt, signature, connector, clock, environment
discovery, or write path.

No existing package may import Slice B. Slice B must not import identity,
interpretation, model, observation/semantic compatibility, constraint,
behavior, state, transition, flow, connector/vendor, UI, planning, control,
private filesystem-store, or private SQLite modules.

Work must stop before implementation if the accepted lower seams cannot
support every captured-view fence required by Section 9. Work must also stop
if exact public field order or `__all__` would require an implementer-chosen
contract that the normative design does not pin.

Both stop conditions are active. See:

`docs/superpowers/reports/2026-09-04-ea001-slice-b-preimplementation-discrepancy-report.md`

## 2. Intended public surface after owner resolution

The package would implement the exact request, route, selection, coverage,
fence, assurance, snapshot, result, validation, and revalidation contracts
named in Sections 11–14, the exact literal vocabularies in Section 12, the
typed exception tree, `EvidenceAssuranceQueries`, and
`validate_operational_evidence_snapshot(...)`.

The facade would expose exactly:

```python
select_operational_evidence(request)
revalidate_operational_evidence(snapshot, *, membership_mode)
```

No convenience or assessment alias would be added. Package exports and every
model field would be tested by exact ordered equality after the missing
contract pins are supplied.

## 3. Intended captured-view sequence

The implementation sequence is fixed:

1. deep-reconstruct and validate the request before dependency access;
2. capture the initial exact-scope source token;
3. capture the initial exact-scope temporal token;
4. obtain temporal material in its one read transaction;
5. derive the optional selected seed attempt ID and read source material once;
6. verify source closure and both parity axes from captured material;
7. capture final source and temporal tokens;
8. refuse on changed token or material/fence disagreement; and
9. derive routes, selection, coverage, issues, assurance, canonical bytes, and
   fingerprint only from the captured material.

The resulting claim is limited to captured-view consistency at observed
fences. It is never described as a distributed transaction, global atomic
snapshot, globally current evidence, or detection after the final fences.

## 4. Intended implementation checkpoints

After owner resolution, development would proceed in reviewable commits:

1. exact public contracts, literal vocabularies, typed errors, and exports;
2. captured-view facade, parity, routes, selection, coverage, issues, and
   canonical snapshot construction;
3. store-independent reconstruction/canonical validation and independently
   retained expected-fingerprint comparison;
4. both store-bound revalidation modes; and
5. adversarial mutation, hostile reconstruction, determinism, import
   isolation, preservation, and no-side-effect hardening.

Before the first production commit, focused import/field/signature/facade
tests would be run red and their output retained. Every genuine post-green
defect would likewise be reproduced by a failing test before repair.

## 5. Intended canonical and result rules

Canonicalization would use sorted Unicode object keys, compact UTF-8 JSON,
`ensure_ascii=False`, finite strict values, aware UTC datetimes rendered with
`+00:00`, and the exact carried `value_json` string. The embedded fingerprint
would be omitted from its own canonical input and returned as lowercase
`sha256:` plus SHA-256 of those bytes.

Issues 1–14 would make the outer result `refused` with no snapshot. Issues
15–16 would remain ordered within an incomplete canonical snapshot. All
applicable issues would be retained in code/routing/detail order even when an
earlier issue controls outer status.

Offline validation would perform no I/O and would disclose source bytes and
temporal-store presence as `not_rechecked`. Store-bound revalidation would
support only `require_equal_final_observed_membership` and
`named_captured_artifacts` after the lower named-artifact capability is
resolved.

## 6. Verification plan

The final gate would include:

- focused Slice B and full EA tests;
- complete data-source and temporal suites;
- architecture/import-isolation and affected downstream suites;
- complete model-kernel and repository suites;
- fresh base-only and all-extras clean checkouts;
- isolated permitted loopback reconciliation when sandboxing prevents the
  existing localhost test;
- backend compilation and dependency checks;
- working-tree and full-milestone `git diff --check`;
- exact 36-record model count, accepted model revision, FRG/FLD/FLW `1/1/0`,
  ledger aggregate, FL disclosure size/digest, accepted historical artifacts,
  and Slice A deterministic lower-material serialization.

The Slice B completion report would remain uncommitted for owner validation.
No Slice C work would begin.

END OF EA-001 SLICE B IMPLEMENTATION PLAN
