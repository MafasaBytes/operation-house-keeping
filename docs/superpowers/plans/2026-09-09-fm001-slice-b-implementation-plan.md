# FM-001 Slice B Implementation Plan

Date: 2026-09-09

Status: executed and owner accepted at exact tested implementation
`4d8219d88d3f5f531c1a1cf250b36cb25e001c2f`; FM-001 complete

Accepted tested-implementation synthesis blob:
`docs/superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md`
at exact implementation `4d8219d88d3f5f531c1a1cf250b36cb25e001c2f`,
SHA-256 `6c1061fe63bf77d0975a4854fb0ba9a462cf03bef6af125d91b3ed43433592f7`.

Accepted Slice A implementation:
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`.

## 1. Scope and stop gate

Slice B may begin only after the owner accepts the exact corrected contract
and separately authorizes implementation. Its complete production scope is
five read-only `ModelQueries` methods, 11 public aliases, four nested public
rows, five outer public results, private derivation/reconstruction helpers,
and exact exports in the existing `backend.model_kernel` package.

Slice B owns no store, database, cache, ledger, identity, record, builder,
fixture, demonstration, authoritative append, evidence selector, temporal
query, observation reader, evaluator, facade, connector, clock, environment
lookup, or write path. It does not modify Slice A records, canonical IDs,
effective bodies, lifecycle, indexes, lower contracts, or authoritative model
data. There is no Slice C.

## 2. Exact query responsibilities

Implement only:

1. `flow_measurement_association(flow_anchor_id, variable_anchor_id, participant_port_anchor_id, context, orientation)`;
2. `flow_measurement_associations_for_flow(flow_anchor_id, *, context)`;
3. `flow_measurement_associations_for_variable(variable_anchor_id, *, context)`;
4. `flow_measurement_associations_at_port(participant_port_anchor_id, *, context)`;
5. `flow_measurement_assertion(record_id)`.

The first method selects one complete immutable v1 subject. The fixed
`direct_measurement_relevance` dimension is implicit and is not a redundant
input. The next three methods use their dedicated flow/context,
variable/context, and port/context indexes. The fifth is a syntactically
bounded `fma_`/`fmw_` assertion lookup. No method is a free-function export,
alias, unbounded scan, store access, or reselection operation.

## 3. Exact public additions

Preserve the accepted 205-name Slice A `backend.model_kernel.__all__` prefix.
Append exactly these 20 names, producing 225 total:

1. `FlowMeasurementEndpointRegistration`;
2. `FlowMeasurementReverseRegistration`;
3. `FlowMeasurementDeclarationPresence`;
4. `FlowMeasurementDeclarationConclusion`;
5. `FlowMeasurementSupportKind`;
6. `FlowMeasurementSupportActivity`;
7. `FlowMeasurementSupportLineageHealth`;
8. `FlowMeasurementSupportAlignment`;
9. `FlowMeasurementOrientation`;
10. `FlowMeasurementAgreementFinding`;
11. `FlowMeasurementAssertionLookupStatus`;
12. `FlowMeasurementSupportRow`;
13. `FlowMeasurementEffectiveBodyGroupRow`;
14. `FlowMeasurementRootRow`;
15. `FlowMeasurementEntryRow`;
16. `FlowMeasurementAssociationResult`;
17. `FlowMeasurementAssociationsForFlowResult`;
18. `FlowMeasurementAssociationsForVariableResult`;
19. `FlowMeasurementAssociationsAtPortResult`;
20. `FlowMeasurementAssertionResult`.

Reuse the accepted public `AssertionActivity`, `ContainingLineageHealth`, and
`FlowPortRole` aliases. Do not add FM duplicates, support presence, semantic-
support summary, result-only orientation, an FM builder, or private helpers to
`__all__`.

## 4. Result construction and carry-once discipline

Every outer result carries exactly one complete `ModelQueryMaterial`. Nested
rows carry only strict indices and subject/derived fields fixed by the
synthesis. They never repeat material, records, context, or record IDs.

All fields are required, even when the normative value is `None` or an empty
tuple. Missing content therefore refuses rather than acquiring a default.
Material index tuples are strictly increasing and unique. Root, group, and
entry indices are non-boolean and contiguous from zero. Every index is range-
checked against its exact containing collection.

The exact lookup carries endpoint registration, declaration presence,
aggregate conclusion, ordered findings, optional derived role, roots, body
groups, and current assertion indices. It carries no singular subject-level
activity or lineage health.

Each reverse entry represents one complete subject in the outer exact context
and carries the same nonconstant subject payload as exact lookup. Different
orientations are different entries. Entries are never split by root or record.

The assertion result distinguishes not-found, found positive, and found
withdrawal shapes through lookup status, record material, and exact null/
empty cardinality. Only a found positive carries activity, containing-root
health, subject conclusion/findings, role, orientation, and six support rows.

## 5. Roots, effective-body groups, and findings

Build roots from the accepted Slice A root/ancestry/tip/withdrawal indexes.
Order roots by root record ID. A root carries its complete lineage indices,
current tip indices, withdrawal indices, health, and every body-group index in
which one of its current tips participates. It never chooses one body.

Group all current tips by the exact private canonical Slice A effective-body
bytes. Order groups by those bytes. Each group carries its lowest-record-ID
representative current tip, all current tips, every participating root index,
the immutable role/orientation, and the six support rows for that body. An
inactive root participates in no group; a conflicted root may participate in
one or several groups.

Retain findings in literal order. Aggregate conclusion precedence is:

1. no declaration -> `not_evaluated`;
2. any same-root conflict or cross-root body-set disagreement -> `conflicted`;
3. otherwise any healthy root -> `declared_direct_measurement_relevance`;
4. otherwise all roots are inactive -> `inactive`.

Healthy, conflicted, inactive, corroborating, and disagreeing findings may
coexist. Nothing selects a winning root, tip, body, authority, timestamp, or
record ID.

## 6. Support-row derivation

Every positive body/selected assertion has exactly six rows in kind order:
FRG, VRG, PRG, FLD, VPA, VSM. A row carries only the exact pinned record
index, pinned-record activity, containing-lineage health, and current
alignment.

FRG/VRG/PRG are permanent, `not_applicable` for lineage health, and `exact`.
FLD/VPA use their accepted root lifecycle: current, superseded, or withdrawn;
healthy, conflicted, or inactive; active lineages remain structurally exact
and inactive lineages are unaligned. VSM is context-independent and has only
current/superseded activity and healthy/conflicted health. Its current
alignment is exact only when every current observation-role tip retains the
exact measured-actual token. VSM never has context, withdrawal, withdrawn
activity, or inactive health.

Any kind/literal combination outside the synthesis reachability table is
malformed result content, not structured evidence absence.

## 7. Reverse ordering and structured absence

Group selected reverse-index record IDs by complete subject before emitting
entries. Use orientation literal rank, not lexicographic order. Exact semantic
ordering keys are:

- flow: variable, participant port, orientation rank;
- variable: flow, participant port, orientation rank;
- port: flow, variable, orientation rank.

An unregistered selected reverse endpoint yields `not_registered`,
`not_declared`, and no entries. A registered endpoint with no exact-context FM
subject yields `registered`, `not_declared`, and no entries. Positive entries
require `registered` and `declared`. The accepted 36-record pre-FM material
must produce structured absence from all five methods without synthetic rows.

## 8. Authoritative reconstruction and hostile schedule

Reconstruct all supplied outer and nested values from plain content. Rebuild
the one carried `ModelQueryMaterial` first through the existing authoritative
kernel path, then derive expected payloads from that reconstructed material.
Do not trust supplied Pydantic instances and do not access rows before their
reconstruction succeeds.

Reject wrong union arms, hidden/private state, `model_construct`,
`model_copy`, scalar subclasses, Boolean/negative/out-of-range indices,
missing/duplicate/extra/reordered rows, stale conclusions/findings, subject or
context substitution, forged IDs/revision/material, cycles, and oversized or
deep graphs through the existing typed model-kernel error boundary. Validation
performs no I/O, write, store query, network access, clock read, or environment
discovery.

## 9. Red-first implementation sequence

After authorization only:

1. commit this accepted plan/matrix/status checkpoint administratively;
2. add exact failing public aliases/models/fields/literals/export tests;
3. add failing structured-absence and positive exact-query tests;
4. implement one private subject-payload builder and exact lookup;
5. add failing body-group/mixed-root tests and implement grouping/findings;
6. add failing support reachability tests and implement support derivation;
7. add failing reverse-entry/order/context tests and implement three indexes;
8. add failing positive/withdrawal/not-found assertion tests and implement it;
9. add hostile reconstruction/carry-once/no-I/O tests before repairs;
10. perform bounded adversarial review and encode each genuine defect red-first;
11. run full working and dual-clean verification at the final runtime commit;
12. write an uncommitted completion report and stop for owner acceptance.

No step authorizes a contract change. A blocking contradiction requires a
discrepancy report and stop.

## 10. Verification and stopping point

Completed implementation verification included the complete FM suite,
model-kernel, identity, affected FL/VP/VS/ES, architecture/isolation, full
working repository, fresh base-only and all-extras checkouts, permitted
loopback reconciliation, CAD/STEP/PDF, five hash seeds, reverse construction,
dependencies, compilation, whitespace, and exact protected-state checks.

The implementation must preserve 36 authoritative records, revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
FRG/FLD/FLW `1/1/0`, TRG/TRD/TRW `0/0/0`, FMA/FMW `0/0`, ledger aggregate
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`,
and every accepted disclosure, lower reproduction, identity, membership,
fixture, record, and artifact.

The accepted completion report is
`docs/superpowers/reports/2026-09-09-fm001-slice-b-completion-report.md` at
SHA-256 `f7ce3280a6d1af1682b6ef1139fc8d8d2166c26e56525c703029f03586d8c290`.
FM-001 is complete; there is no Slice C or demonstration, and FA-001 remains
separate and unauthorized.

END OF FM-001 SLICE B IMPLEMENTATION PLAN
