# EA-001 Slice B Contract Correction Report

Date: 2026-09-05

Status: bounded design-contract correction complete; owner approval pending;
Slice A integrity repair and Slice B implementation remain paused

## 1. Authority and outcome

The owner accepted the EA-001 Slice B preimplementation discrepancy stop at:

`b3e27cb41d9d69bf1545b50fb5aaa693ca7586f6`

The accepted discrepancy report is:

`docs/superpowers/reports/2026-09-04-ea001-slice-b-preimplementation-discrepancy-report.md`

Its accepted SHA-256 is:

`cc5999e2d1f4d7191b4c4dba047f4420793f86a03f7b7cbe1801116dde486574`

The owner authorized only a bounded design-contract correction. The corrected
synthesis and plan now resolve all four reported discrepancies. No production
code, test, fixture, source evidence, temporal data, model record, ledger,
membership, canonical artifact, lead proposal, challenger audit, accepted
Slice A report, or accepted discrepancy report was modified.

## 2. Corrected artifacts

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `docs/superpowers/specs/2026-09-04-ea001-content-bound-operational-evidence-selection-and-assurance-design.md` | 85,824 | `557b2df9aec5ee784006bfdba771936ae90844ea7cf8913c1e61455fa4a7e08e` |
| `docs/superpowers/plans/2026-09-04-ea001-slice-b-implementation-plan.md` | 9,598 | `419e25c6cc752356292fdaeb98d635b01140d718f0aff2271379665a7fb93bd5` |

The synthesis retains its exact ending marker:

`END OF EA-001 FINAL SYNTHESIS`

The plan retains its exact ending marker:

`END OF EA-001 SLICE B IMPLEMENTATION PLAN`

## 3. Resolution one — seed-aware source fence

The public token signature remains unchanged. No caller-supplied seed ID is
added. Each source inventory-token invocation independently discovers the
exact source-side latest eligible exact-property observation at/before
`as_of`, using receipt time and the complete `AttemptOrderKey`.

When the candidate is pre-horizon, the token binds exactly one candidate and
its complete mechanical closure: attempt, attempt run, raw envelope,
originating run for reused content, raw payload, extraction result, exact
observation-bearing extraction content, and every required dependency. It
uses the accepted member-key, same-read digest, byte-count, and payload-
checksum rules.

Historical discovery is streaming and bounded per artifact. It does not count
all lifetime attempts against the retained 4,096 in-horizon limit. Distinct
attempts remain distinct candidates even when they reuse one raw payload.

The temporal-selected seed ID later supplied to `read_material(...)` must
equal the independently discovered source candidate. Lower disagreement is
`OPERATIONAL_EVIDENCE_SEED_PARITY_MISMATCH`; EA maps it to
`source_temporal_parity_failure`. No temporal import enters `data_sources`.

## 4. Resolution two — exact named-material reread

The existing reader protocol and filesystem implementation gain exactly:

```python
reread_named_material(
    expected_material: Ds004OperationalEvidenceMaterial,
) -> Ds004OperationalEvidenceMaterial
```

The method deep-reconstructs expected material before I/O, accepts no path,
derives exact names from artifact kind/logical ID, rereads only the carried
set, hashes/parses metadata from the same bytes, rereads payload bytes against
stored checksums, rebuilds complete material, and requires exact equality.

Unrelated additions are ignored. Current horizon growth—including growth
beyond the ordinary capture bound—does not prevent the named reread. The
frozen artifact-count and retained-metadata-byte bounds still apply. Typed
errors distinguish named material unavailable from changed/invalid. Current
membership remains a separate `inventory_token(...)` observation.

No lower exported name is added: `backend.data_sources.evidence.__all__`
remains the two accepted reader types, with the new method on each.

## 5. Resolution three — exact result/support models

The synthesis now pins field order, types, strict bounds, reconstruction, and
invariants for every formerly referenced support/result model:

- `OperationalEvidenceMaterialLimits`;
- `OperationalEvidenceIssue`;
- `OperationalNamedArtifactRevalidation`;
- `OperationalEvidenceSelectionResult`;
- `OperationalEvidenceStoreRevalidationResult`; and
- `OperationalEvidenceSnapshotValidationResult`.

The store result carries only status/mode, snapshot fingerprint, structural
status, expected artifact/route counts, named/temporal/current-membership
relations, strict named-artifact rows, and revalidation issues. It repeats no
snapshot or complete source/temporal material. Offline validation similarly
repeats no snapshot and always discloses both store axes as `not_rechecked`.

All nested content is rebuilt from plain serialized values with cycle,
extra-field, union-arm, boolean-index, range, uniqueness, ordering, closure,
derived-value, canonical-byte, and fingerprint checks.

## 6. Carry-once and state-table pins

The corrected selection table requires:

- complete or incomplete: one snapshot, empty outer issues, and snapshot-only
  incomplete issues;
- refused: no snapshot and result-only refusal issues; and
- no issue duplication between result and snapshot.

The corrected revalidation table distinguishes:

- named source material `matched`, `changed`, `unavailable`, or
  `not_evaluated`;
- captured temporal material `matched`, `changed`, `not_fully_observed`, or
  `not_evaluated`;
- source and temporal membership separately as equal to the snapshot final
  token, different, not fully observed, or not evaluated; and
- all four accepted outer revalidation statuses in normative order.

Exact named equality may return `valid_for_named_captured_artifacts` when
current membership differs or cannot be fully observed. Its relation fields
make those limitations explicit, and it never calls the older selection
current or latest.

## 7. Exact vocabularies and errors

The original 16 issue codes and their rank are retained. Codes 1–14 refuse;
codes 15–16 may inhabit only an incomplete snapshot. Issues sort by rank,
`None`-before-integer route index, and detail code.

All selection, offline validation, expected/embedded fingerprint, membership
mode, store revalidation, named-material, carried-temporal-material, and
observed-membership literals are pinned in exact normative order.

EA exceptions expose exactly `error_code` and `message`. Configuration misuse
is only `EA_DEPENDENCY_INVALID`. Query misuse is only `EA_REQUEST_INVALID` or
`EA_SELECTION_POLICY_INVALID`. Messages are bounded and redacted.

## 8. Exact public exports

The corrected synthesis pins `backend.evidence_assurance.__all__` to exactly
33 ordered names: the three errors, two error-code aliases, canonical age
type, coverage/issue/status/relation vocabularies, request/material/route/
coverage/selection/fence/assurance/snapshot/result models, the facade, and the
pure validator.

No lower source/temporal type is re-exported. No convenience, authentication,
assessment, current, freshness, history, occurrence, transition, or flow alias
is allowed.

## 9. Resolution four — cross-clock vocabulary

EA-001 v1 has no cross-clock comparison input, method, result, or exception
path. The former cross-clock error is removed from the exact error union.

Policy always carries `source_time_use="disclosure_only"`. Any malformed or
altered policy raises `EA_SELECTION_POLICY_INVALID` before I/O. Source-time
markers and clock openings remain carried disclosure and never select, filter,
order, or change coverage/status.

Old A21 is retained by number with an explicit final disposition: tests prove
the API absence, fixed disclosure-only policy, policy-misuse error, and lack
of any source-time selection effect. No requirement disappears silently.

## 10. Revised captured-view and revalidation protocols

Selection now brackets the temporal transaction and source read with source
tokens that each independently rediscover the seed. Material/fence equality
and independent source/temporal seed parity are mandatory before derivation.
Any seed dependency mutation at A31–A33 changes a token or refuses typed.

Store-bound revalidation first performs pure validation, then one exact named
source reread, then separate current source/temporal membership observations
and bounded carried-temporal-row checks. Equality mode requires stable equality
with the snapshot's final tokens. Named mode limits its success claim to the
named source material and discloses every current/temporal limitation.

Neither protocol claims a distributed transaction, global atomic snapshot,
globally current evidence, or detection after final fences.

## 11. Acceptance-matrix reconciliation

The synthesis keeps A01–A50. Corrections are explicit in:

- A03: exact named reread, unrelated additions, and over-bound current growth;
- A04 and A31–A33: every pre-horizon seed dependency at each source boundary;
- A21: removed cross-clock API mapped to disclosure-only policy tests;
- A28: exact fixed limits and streaming seed discovery;
- A36: crossed mutation plus independently discovered seed parity;
- A40: exact fields and package exports;
- A43: named/unavailable/not-fully-observed distinctions;
- A45: all public/result/lower-reread hostile and carry-once boundaries; and
- A48: exact offline no-I/O fields and no repeated snapshot.

The remaining rows preserve their accepted meaning.

## 12. Owner-gated sequencing

No implementation resumes from this report. After owner acceptance of the
corrected contract, the next separately authorized unit is only the Slice A
integrity repair:

1. automatic source-side pre-horizon seed discovery/token binding;
2. source/temporal seed-ID agreement;
3. exact named-material reread;
4. focused hostile/deterministic/no-side-effect regression tests; and
5. updated lower reproduction evidence if token serialization changes.

That repair must receive its own completion report and owner acceptance.
Slice B remains paused until then. Slice C remains unauthorized.

## 13. Preservation, scope, and owner gate

This correction adds no architecture layer, production behavior, store,
schema, projector, cache, ledger, revision, anchor, identity, minter,
signature, receipt, network/connector path, clock comparison, semantic or
assessment integration, durable artifact, authority endorsement, trusted
time, physical-occurrence result, or truth claim.

Only the corrected synthesis, its dependent implementation plan, and this new
report are changed. The lead proposal, challenger audit, accepted Slice A
completion report, and accepted discrepancy report remain byte-exact.

There are no unresolved contract-design questions inside this candidate. The
sole owner decision is whether to accept the exact corrected synthesis and
this report. That acceptance would not authorize the Slice A repair or resume
Slice B.

END OF EA-001 SLICE B CONTRACT CORRECTION REPORT
