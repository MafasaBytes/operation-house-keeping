# FM-001 Slice B Contract Correction Report

Date: 2026-09-09

Status: corrected public-contract candidate complete; Slice B implementation
unauthorized pending owner approval and separate authorization

## 1. Disposition

This documentation-only checkpoint records owner acceptance of repaired
FM-001 Slice A and corrects the future Slice B result contract without
implementing it. The accepted architecture, five query responsibilities,
direct-measurement truth boundary, participant-port locus, exact same-revision
support closure, context-independent VSM, and two-slice milestone remain
unchanged.

No new architecture proposal, challenger pass, production code, behavioral
test, fixture, ledger member, model revision, identity, demonstration,
authoritative append, facade, or upper-layer consumer was added. There is no
Slice C.

## 2. Starting checkpoint

Work began on branch `fm001` at exact repaired Slice A implementation
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`. The only working-tree item was
the reviewed untracked completion report. Its 363 lines and 17,533 UTF-8 bytes
were preserved byte-identically at SHA-256
`93c089269b90499de1b7aabf748c13a7f5ba53d5898bdea80347ce9eb6a460de`.

The branch, ancestry, report marker, protected state, and working status were
checked before mutation. `.claude/settings.local.json` remained outside the
milestone at SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

## 3. Slice A administrative acceptance

The documentation-only commit
`6625fb89b49235444887b285f98eb7bc6a2ab7f0` (`docs: accept FM-001 Slice A`)
commits the frozen report, adds
`docs/superpowers/reports/2026-09-09-fm001-slice-a-owner-acceptance.md`, and
updates only current status/module wording. The acceptance record is SHA-256
`81692c708b10f6f11591b9d8bf987c510c90cd5760f5e5141365a7956f92d869`.

That record accepts the exact tested Slice A records, integrity, indexes,
replay, deterministic witness, verification, and repaired distinct-active-root
comparison. It does not accept all FM-001 and does not authorize Slice B.

## 4. Corrected authorities and digest transition

The accepted pre-correction synthesis was SHA-256
`baca77b5c6080075f8dc59ba58c0574d6421cc27eb1b9a3d899883be3e5e0d18`.
The corrected synthesis is SHA-256
`6c1061fe63bf77d0975a4854fb0ba9a462cf03bef6af125d91b3ed43433592f7`.

The pre-correction ADR-0021 file was SHA-256
`b9fe17dbd59fce45e10ee8cd0f18008be1cdb7ecb1f1c1bae10cb1134538ce15`.
The corrected ADR-0021 is SHA-256
`71bb00e57132e982fb4243968c24f8b5b24072da03c879bb3d61ac5b1d56d671`.
Its formerly stale inline synthesis digest is replaced with the exact
corrected digest; historical accepted reports remain unchanged.

The synthesis retains its exact ending marker, 25 contiguous numbered
sections, and all accepted Slice A record, canonical, lifecycle, and truth-
boundary contracts. Only the inconsistent future Slice B result sketch,
associated acceptance rows, sequencing/status language, and consequences were
corrected.

## 5. Exact public aliases

Slice B adds exactly these 11 aliases, in this public/export order:

1. `FlowMeasurementEndpointRegistration`: `all_registered`,
   `flow_not_registered`, `variable_not_registered`, `port_not_registered`,
   `multiple_not_registered`;
2. `FlowMeasurementReverseRegistration`: `not_registered`, `registered`;
3. `FlowMeasurementDeclarationPresence`: `not_declared`, `declared`;
4. `FlowMeasurementDeclarationConclusion`: `not_evaluated`,
   `declared_direct_measurement_relevance`, `conflicted`, `inactive`;
5. `FlowMeasurementSupportKind`: `frg`, `vrg`, `prg`, `fld`, `vpa`, `vsm`;
6. `FlowMeasurementSupportActivity`: `permanent`, `current`, `superseded`,
   `withdrawn`;
7. `FlowMeasurementSupportLineageHealth`: `not_applicable`, `healthy`,
   `conflicted`, `inactive`;
8. `FlowMeasurementSupportAlignment`: `exact`, `unaligned`;
9. `FlowMeasurementOrientation`: `aligned`, `opposite`,
   `unsigned_magnitude`, `not_applicable`;
10. `FlowMeasurementAgreementFinding`: `one_healthy_root`,
    `corroborating_healthy_roots`, `same_root_conflict`,
    `inactive_roots_present`, `cross_root_effective_body_disagreement`;
11. `FlowMeasurementAssertionLookupStatus`: `not_found`, `found`.

The existing `AssertionActivity`, `ContainingLineageHealth`, and
`FlowPortRole` aliases are reused. The correction removes duplicate FM
lineage/activity/role aliases, the constant support-presence axis, the
duplicated semantic-support summary, the former activity-bearing alignment
token, and result-only orientation/status values with no valid-world witness.

## 6. Exact nested models

Slice B adds exactly four required-field, extra-forbidding nested models:

1. `FlowMeasurementSupportRow`: `support_kind`, `record_index`, `activity`,
   `containing_lineage_health`, `current_alignment`;
2. `FlowMeasurementEffectiveBodyGroupRow`: `group_index`,
   `representative_current_tip_index`, `current_tip_indices`,
   `participating_root_indices`, `participant_role`, `orientation`,
   `support_rows`;
3. `FlowMeasurementRootRow`: `root_index`, `root_record_index`,
   `lineage_record_indices`, `current_tip_indices`, `withdrawal_indices`,
   `lineage_health`, `effective_body_group_indices`;
4. `FlowMeasurementEntryRow`: `entry_index`, `flow_anchor_id`,
   `variable_anchor_id`, `participant_port_anchor_id`, `orientation`,
   `declaration_conclusion`, `agreement_findings`, `participant_role`,
   `roots`, `effective_body_groups`, `current_assertion_indices`.

All empty tuples are explicit. Material indices are strict, non-Boolean,
nonnegative, in range, unique where plural, and ordered by selected material.
Root/group/entry indices are strict and contiguous in their own containing
tuples. Nested rows never carry material, context, records, or duplicate IDs.

## 7. Exact outer models and carry-once shapes

The five outer public result names remain unchanged:

1. `FlowMeasurementAssociationResult`: `material`, `flow_anchor_id`,
   `variable_anchor_id`, `participant_port_anchor_id`, `context`,
   `orientation`, `endpoint_registration`, `declaration_presence`,
   `declaration_conclusion`, `agreement_findings`, `participant_role`,
   `roots`, `effective_body_groups`, `current_assertion_indices`;
2. `FlowMeasurementAssociationsForFlowResult`: `material`, `flow_anchor_id`,
   `context`, `registration_status`, `declaration_presence`, `entries`;
3. `FlowMeasurementAssociationsForVariableResult`: `material`,
   `variable_anchor_id`, `context`, `registration_status`,
   `declaration_presence`, `entries`;
4. `FlowMeasurementAssociationsAtPortResult`: `material`,
   `participant_port_anchor_id`, `context`, `registration_status`,
   `declaration_presence`, `entries`;
5. `FlowMeasurementAssertionResult`: `material`, `record_id`,
   `lookup_status`, `record_index`, `assertion_activity`,
   `containing_root_health`, `containing_subject_conclusion`,
   `containing_agreement_findings`, `root_record_index`,
   `successor_indices`, `withdrawal_indices`, `participant_role`,
   `orientation`, `support_rows`.

Every field is required, including explicit `None` and empty-tuple arms. Each
outer carries exactly one complete `ModelQueryMaterial`. Exact absence,
reverse unregistered/registered-empty, assertion not-found, positive, and
withdrawal results have disjoint exact cardinalities. Subject results do not
invent one assertion activity or root health when several roots exist; an
individual positive assertion may disclose its own activity and containing-
root health.

## 8. Exact query and reverse-entry contract

The five methods remain exactly:

1. `flow_measurement_association(...)`;
2. `flow_measurement_associations_for_flow(...)`;
3. `flow_measurement_associations_for_variable(...)`;
4. `flow_measurement_associations_at_port(...)`;
5. `flow_measurement_assertion(...)`.

The exact method accepts flow, variable, participant port, context, and
orientation; direct-measurement relevance is the fixed implicit v1 relation.
The three reverse methods use only their respective flow/context,
variable/context, and port/context immutable indexes. Assertion lookup is
separate and accepts only a syntactically valid `fma_` or `fmw_` identifier.

One reverse entry represents one complete immutable FMA subject in the outer
exact context, regardless of root or record count. Different orientations are
different entries. Flow entries order by variable/port/orientation rank,
variable entries by flow/port/orientation rank, and port entries by
flow/variable/orientation rank. Cross-context material is excluded. No method
is an alias, unbounded scan, free-function export, recursive public query, or
store operation.

## 9. Support reachability correction

Each positive effective-body group and found positive assertion carries
exactly six support rows ordered FRG, VRG, PRG, FLD, VPA, VSM. Absence,
not-found, withdrawal, and root-only disclosures carry no fabricated rows.

- FRG/VRG/PRG are always `permanent` / `not_applicable` / `exact`.
- Current FLD/VPA pins are `current`, healthy or conflicted, and `exact`.
- Superseded or withdrawn FLD/VPA pins are healthy/conflicted and `exact`
  while their lineage stays active, or inactive and `unaligned` when it does
  not.
- VSM is current or superseded and healthy or conflicted. It is `exact` only
  when every current context-independent observation-role tip retains the
  exact measured-actual token; otherwise it is `unaligned`.

VSM has no assertion context, withdrawal record, withdrawn activity, or
inactive health. Permanent registrations have no supersession, withdrawal,
conflict, or inactive lifecycle. Activity, containing-lineage health, and
current alignment remain orthogonal fields; stale or unaligned support is
disclosure, not a physical or truth judgment.

## 10. Root, body-group, and mixed-root correction

A root row discloses exactly one lineage and every body-group index reached by
its current tips. It does not select a body or support set. A body-group row
discloses one canonical Slice A effective body, all matching current tips and
participating roots, one lowest-record-ID representative for reconstruction,
the immutable role/orientation, and six support rows. The representative is
not authority and does not select a winner.

A conflicted root can reach one or several groups. Independent roots can share
one group and corroborate, or carry unequal active body sets and disagree.
Healthy-plus-conflicted and conflicted/disagreeing combinations retain all
applicable findings and conclude `conflicted`. Healthy-plus-inactive retains
both findings and remains positively declared. All-inactive roots stay
visible, have no active groups, and conclude `inactive`.

Conclusion precedence is no declaration, then any same-root conflict or
cross-root body-set disagreement, then any healthy root, then all inactive.
Findings are retained in exact alias order and coexist; no status hides a
lower fact and no root, body, support set, authority, timestamp, or ID wins.

## 11. Authoritative reconstruction and refusal

Every supplied result is first reduced to plain content and reconstructs its
one carried material through the existing model-kernel revalidation and
`validate_record_collection` authority. Only validated material may support
record access or private derivation. The same private subject-payload builder
must drive exact, reverse, and assertion disclosures.

Reconstruction recomputes subjects, registration, role, roots, tips,
withdrawals, bodies, groups, supports, lifecycle, alignments, conclusions,
findings, indices, and deterministic order. It rejects forged Pydantic
instances, hidden state, wrong union arms, scalar subclasses, Boolean or
invalid indices, stale/extra/missing/reordered/substituted rows, contexts,
IDs, revisions, material, cycles, depth, and size at the accepted typed query
boundary. Validation performs no I/O, store query, network access, clock or
environment read, or write and adds no second graph validator.

## 12. Exact export correction

The accepted Slice A `backend.model_kernel.__all__` prefix remains exactly 205
names. Slice B would append the 11 aliases from Section 5, followed by
`FlowMeasurementSupportRow`, `FlowMeasurementEffectiveBodyGroupRow`,
`FlowMeasurementRootRow`, `FlowMeasurementEntryRow`,
`FlowMeasurementAssociationResult`,
`FlowMeasurementAssociationsForFlowResult`,
`FlowMeasurementAssociationsForVariableResult`,
`FlowMeasurementAssociationsAtPortResult`, and
`FlowMeasurementAssertionResult`.

That is exactly 20 ordered additions and 225 total exports. Query methods,
private helpers, duplicate aliases, public builders, stores, facades, and
convenience names are excluded.

## 13. Future plan and acceptance reconciliation

The corrected implementation plan is
`docs/superpowers/plans/2026-09-09-fm001-slice-b-implementation-plan.md`, 218
lines, 10,568 UTF-8 bytes, SHA-256
`1bf6c8835d799186795478c337e12df9446e0b16d494d412604d07d6717922f2`.

The corrected adversarial matrix is
`docs/superpowers/plans/2026-09-09-fm001-slice-b-adversarial-acceptance-matrix.md`,
120 lines, 9,600 UTF-8 bytes, SHA-256
`6f4d6927b41bb97089c4b4277c064b9cc6371ffa68375b36af36954d617c8200`.
FM-B01–FM-B58 map exact surface, absence, mixed roots, support reachability,
reverse semantics, assertion disclosure, hostile reconstruction, carry-once,
purity, determinism, and preservation. Each future behavioral row requires a
failing-before test and a valid twin after separate implementation
authorization. The synthesis's FM-A01–FM-A58 matrix is reconciled to the same
contract.

## 14. Documentation verification

The final focused documentation/status and flow-architecture gate passed 32
tests in 18.01 seconds before this correction commit. Exact searches confirmed 11
aliases, four nested models, five outer results, five methods, 20 additions,
225 total exports, three reverse indexes, and 58 future FM-B rows. Obsolete
aliases, impossible state literals, placeholders, accidental alternate names,
and stale four-reverse wording were absent from current authority.

Local relative-link validation covered every changed Markdown document.
Numbered sections and ending markers were checked for the synthesis, ADR,
acceptance record, plan, matrix, and this report. Working and full FM milestone
range `git diff --check` completed without diagnostics. No full repository or
clean-checkout suite was required or claimed for this documentation-only
correction.

## 15. Protected-state preservation

Direct read-only checks after the documentation correction found exactly 36
authoritative record files at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FRG/FLD/FLW remains `1/1/0`, TRG/TRD/TRW remains `0/0/0`, and authoritative
FMA/FMW remains `0/0`. The whole-ledger aggregate remains
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.

The FL disclosure remains exactly 660,516 bytes at SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.
The two context-independent VSM files remain at SHA-256
`371527c7bd45c3118043b3da3ab2f17bb34769eacea4dd48e84eb148c71ea33a`
and `b04377e1a5385a2a301ef288a0a211fcf06602914a36a2da334615915659730f`.
The accepted lower reproductions, TA result, identities, memberships,
evidence, fixtures, ledgers, revisions, disclosures, canonical artifacts, and
settings are unchanged.

The correction range changes documentation only. No production file,
behavioral test, fixture, evidence, ledger, identity, membership, model
record, canonical artifact, or generation logic changed.

## 16. Scope and owner gate

Repaired Slice A is accepted. The exact corrected Slice B public contract is a
candidate for owner approval, but Slice B implementation remains unauthorized.
No Slice B completion report exists. No Slice C, demonstration, append,
fixture, second consumer, FA-001 work, or later milestone is authorized.

The sole unresolved owner decision is: approve this corrected Slice B public
contract and separately authorize Slice B implementation?

END OF FM-001 SLICE B CONTRACT CORRECTION REPORT
