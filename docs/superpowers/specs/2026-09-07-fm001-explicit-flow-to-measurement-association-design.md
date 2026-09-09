# FM-001 — Explicit Flow-to-Measurement Association

Corrected final synthesis — design only

## 1. Status, inputs, and baseline

Status: owner-accepted design and repaired Slice A; corrected Slice B public
contract pending owner approval; Slice B implementation unauthorized.

This synthesis is based on `main` at
`a069cb664af1638cef2168ced6034eb2d30f2f14`.

Frozen lead proposal:
`docs/superpowers/proposals/2026-09-07-fm001-codex-lead-proposal.md`, 578
lines, 30,026 UTF-8 bytes, SHA-256
`2e8e69b465defe2e9610bb1a34e85b80cc20cdd2a668dc0d01eb119818bf36f2`, ending
`END OF FM-001 CODEX LEAD PROPOSAL`.

Frozen challenger audit:
`docs/superpowers/reports/2026-09-07-fm001-codex-lead-proposal-challenger-audit.md`,
625 lines, 37,054 UTF-8 bytes, SHA-256
`84079ebe361de207819b4d964435cf163dddfdfd97109eb6a40928fb1f6d0bd3`, with
19 numbered sections and ending
`END OF FM-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT`.

The post-TA-001 reconciliation is SHA-256
`c07bd4311d4dbe0345fd877d41a6b9cc7005396dc2c09fd6e2dca85beb09a2fa`.
At that design baseline ADRs 0001–0020 were contiguous and unique and
ADR-0021 was absent; ADR-0021 now records the accepted architecture. The accepted
model has 36 records at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
FRG/FLD/FLW `1/1/0`, TRG/TRD/TRW `0/0/0`, and ledger aggregate
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.
The FL disclosure SHA-256 is
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`; the
accepted TA result SHA-256 is
`1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97`.

## 2. Change log: B1–B5 blockers

| Audit item | Final normative resolution |
|---|---|
| B1 — broad measurement vocabulary collapses unlike dimensions | Section 8 freezes direct-measurement relevance only, using the existing `measured_actual` observation-role declaration; command, estimate, derived, amount, and rate meanings are excluded. |
| B2 — subject permits semantic identity drift | Section 7 freezes flow, variable, participant port, exact context, direct-measurement relevance, and orientation as immutable subject dimensions. Any change starts a new root. |
| B3 — aggregate/whole-flow locus is not implementation-ready | Section 9 permits only one registered participant PortAnchor from the FRG signature; null, aggregate, whole-flow, storage, and control-volume loci are forbidden. |
| B4 — citable withdrawal contradicts accepted withdrawals | Section 11 defines an uncitable `FlowMeasurementAssociationWithdrawal` with no evidence field, following PT/VP/FL precedent. |
| B5 — optional support pins and sibling-ledger references invert ownership | Section 10 requires the exact same-ledger six-record support matrix and excludes source interpretation, semantic compatibility, EA, alignment, TA, temporal, and sibling-ledger pins. |

## 3. Change log: RC1–RC10 corrections

| Audit item | Final normative resolution |
|---|---|
| RC1 — derive boundary role | Source/sink is derived from immutable FRG membership and never stored as an asserted FM body field. |
| RC2 — fix support closure | Exact same-revision FRG, VRG, PRG, FLD, VPA, and measured-actual VSM pins are mandatory. |
| RC3 — fix model semantic/value policy | Direct measurement requires exact `measured_actual` VSM support; VSP, quantity-kind, units, and conversion remain outside FM admission. |
| RC4 — make sign/orientation explicit | The immutable orientation literal set is `aligned`, `opposite`, `unsigned_magnitude`, `not_applicable`; no positive unknown token exists. |
| RC5 — separate result axes | Endpoint admission, declaration presence/conclusion, per-root health, individual assertion activity, support activity/health/current alignment, derived role, orientation, and agreement findings are separate fields. |
| RC6 — complete lineage rules | Parents must be membership-present positive FM records in the same subject and derived root; complete same-root convergence is allowed and cross-root convergence is rejected. |
| RC7 — define exact body identity | Effective-body grouping includes all six support-pin IDs and immutable body dimensions, while excluding evidence, authority, recorded time, note, ID, and ancestry. |
| RC8 — preserve withdrawal behavior | A withdrawal targets one eligible current tip; sibling fork tips do not block selective withdrawal; withdrawal is inactive, not false or non-measurement. |
| RC9 — tighten query contract | Exact lookup includes every caller-variable subject dimension including orientation; relation is the fixed v1 dimension, the three reverse lookups use non-overlapping exact-context indexes, and assertion lookup is separate. |
| RC10 — add hostile twins | Acceptance rows cover cross-lineage correction, body/support/citability substitution, role/orientation drift, context, duplicates, supersession, and no-I/O validation. |

## 4. Change log: NB1–NB5 observations

| Audit item | Final normative resolution |
|---|---|
| NB1 — healthy versus current | `healthy` is lineage health; `current` is assertion or support-pin activity. They are never one aggregate boolean. |
| NB2 — conversion/arithmetic exclusion | FM performs no conversion, arithmetic, dimensional algebra, rate, amount, or aggregation. |
| NB3 — five-query surface | Exactly five query responsibilities are frozen; the participant-port reverse lookup is a real indexed operation, not an alias or scan. |
| NB4 — future prefix/class/evidence arm | Prefixes, classes, record kinds, and the evidence-union arm are frozen in Section 12 only after enumerating all accepted prefixes. |
| NB5 — no demonstration | No demonstration or authoritative append is part of FM-001; every positive world remains disposable and separately gated. |

## 5. Owner decisions D1–D8

1. **D1 — ownership and identity:** FM belongs in `backend.model_kernel` and
   adds no ledger and no durable association anchor.
2. **D2 — subject and locus:** each assertion names one existing FlowAnchor,
   VariableAnchor, registered participant PortAnchor from that flow's FRG,
   exact AssertionContext, direct-measurement relevance, and orientation.
3. **D3 — relationship and boundary role:** v1 is direct-measurement relevance
   only; source/sink is derived from FRG and is not stored.
4. **D4 — orientation:** exactly one of the four literals in Section 8 is
   immutable; unknown is represented by status absence, never a positive token.
5. **D5 — support:** the same-revision six-record matrix in Section 10 is
   mandatory; FRG/VRG/PRG and VSM are context-independent support, while FLD
   and VPA carry the exact FMA assertion context; no PCN/PIF duplication or
   sibling/upper pin is allowed.
6. **D6 — lifecycle:** the established correction-DAG and uncitable withdrawal
   rules in Section 14 apply exactly.
7. **D7 — queries:** exactly the five names and orthogonal result axes in
   Sections 16–18 are public; Slice B implementation remains separately gated.
8. **D8 — slices:** only the two owner-gated slices in Section 24 exist; no
   Slice C and no demonstration are authorized.

## 6. Objective and strongest claim

FM-001 v1 states exactly:

> In this selected model revision and exact assertion context, an authority
> declares that this registered model variable has direct-measurement
> relevance to this registered logical flow at this registered participant
> port, under this explicit orientation, supported by the cited historical
> model records.

The positive record conclusion literal is
`declared_direct_measurement_relevance`.

## 7. Non-objectives and truth boundary

The record never means that an observation occurred at the port, that a sensor
is physically located there, that the variable currently has a value, that a
value is a rate or amount, that units are compatible, that the logical flow
occurred, persisted, or is active, or that the participant is a physical
boundary or control volume. It does not evaluate sign, conservation,
causality, correctness, safety, diagnosis, or recommendation.

FM is a model declaration. It does not select evidence, read temporal stores,
invoke EA or TA, append truth from observations, or establish physical flow.

## 8. Exact positive contract

The exact positive public class is `FlowMeasurementAssociation`. Its record
kind is `flow_measurement_association`; its collision-free prefix is `fma_`.
Its ID regex is `^fma_[0-9a-f]{64}$`.

Fields occur in this exact serialization order and have these exact types:

1. `record_kind: Literal["flow_measurement_association"]`;
2. `schema_version: Literal["1"]`;
3. `record_id: str` matching `^fma_[0-9a-f]{64}$`;
4. `flow_anchor_id: str` matching `FLOW_ANCHOR_ID_PATTERN`;
5. `variable_anchor_id: str` matching `VARIABLE_ANCHOR_ID_PATTERN`;
6. `participant_port_anchor_id: str` matching `PORT_ANCHOR_ID_PATTERN`;
7. `context: AssertionContext`;
8. `orientation: Literal["aligned", "opposite", "unsigned_magnitude", "not_applicable"]`;
9. `flow_registration_record_id: str` matching `^frg_[0-9a-f]{64}$`;
10. `variable_registration_record_id: str` matching `^vrg_[0-9a-f]{64}$`;
11. `port_registration_record_id: str` matching `^prg_[0-9a-f]{64}$`;
12. `flow_declaration_record_id: str` matching `^fld_[0-9a-f]{64}$`;
13. `variable_port_association_record_id: str` matching `^vpa_[0-9a-f]{64}$`;
14. `variable_semantic_declaration_record_id: str` matching `^vsm_[0-9a-f]{64}$`;
15. `evidence: tuple[EvidenceRef, ...]`, non-empty and canonicalized;
16. `supersedes: tuple[str, ...]`, canonicalized `fma_` IDs, default empty;
17. `recorded_at: UtcDatetime`;
18. `authority: AuthorityRef`;
19. `note: str`, default empty.

The model is frozen, extra-forbidden, and reconstructs nested values from plain
content before validation. The direct-measurement dimension is fixed by the
record kind and the mandatory VSM support; it is not an additional mutable
field.

## 9. Exact withdrawal contract

The exact withdrawal public class is
`FlowMeasurementAssociationWithdrawal`. Its record kind is
`flow_measurement_association_withdrawal`; its collision-free prefix is
`fmw_`; its ID regex is `^fmw_[0-9a-f]{64}$`.

Fields occur in this exact order:

1. `record_kind: Literal["flow_measurement_association_withdrawal"]`;
2. `schema_version: Literal["1"]`;
3. `record_id: str` matching `^fmw_[0-9a-f]{64}$`;
4. `withdraws: str` matching `^fma_[0-9a-f]{64}$`;
5. `recorded_at: UtcDatetime`;
6. `authority: AuthorityRef`;
7. `note: str`, default empty.

It has no evidence field, is not accepted by `ModelRecordEvidence`, and is
uncitable by design. It is a non-claim that retracts one eligible current
positive tip; it does not claim false, impossible, or non-measurement.

The accepted prefix inventory is `anc/iba/ibr/ibc/ibj`, `reg/rtd/rel/rwd`,
`vrg/vsp/vsm`, `crg/vcn`, `brg/bhd/bhw`, `srg/std/stw`, `trg/trd/trw`,
`frg/fld/flw`, `prg/pif/pcn/pcm/ptw`, and `vpa/vpw`. `fma` and `fmw` are the
two unused three-letter prefixes selected for FM-001. No other prefix is
allocated.

## 10. Immutable subject and effective body

The immutable lineage subject key is exactly:

```text
(flow_anchor_id,
 variable_anchor_id,
 participant_port_anchor_id,
 context,
 direct_measurement_relevance,
 orientation)
```

`direct_measurement_relevance` is the fixed v1 dimension represented by the
record kind and exact measured-actual VSM support. The participant port must
belong to the FRG source or sink signature. Changing any subject component
starts a new parentless root and cannot be an in-lineage correction.

The exact effective-body key is:

```text
(subject key,
 flow_registration_record_id,
 variable_registration_record_id,
 port_registration_record_id,
 flow_declaration_record_id,
 variable_port_association_record_id,
 variable_semantic_declaration_record_id)
```

Effective-body equality excludes `record_id`, `supersedes`, `evidence`,
`recorded_at`, `authority`, and `note`. Support-pin IDs are included, so
different historical support cannot collapse into one body. Subject fields
remain immutable even when bodies differ.

## 11. Participant locus and derived role

The only v1 locus is one registered participant PortAnchor from the exact FRG
source or sink port set. Null, empty, aggregate, whole-flow, storage,
control-volume, and boundary sentinels are invalid.

The derived participant role is exactly `source` or `sink`, obtained from the
selected FRG's immutable source/sink sets. It is never serialized in the FM
positive body and cannot be forged by a caller. A port appearing in both FRG
sets is structurally invalid in the existing flow contract. A port absent from
both sets refuses.

Fan-in and fan-out use separate atomic assertions. FM does not manufacture
pairwise branches, conservation, balance, or equal values from a directed
hyperedge. A physical sensor locus is not established by the declared port.

## 12. Direct measurement and orientation semantics

The only v1 relationship is direct measurement relevance. The exact model-side
VSM declaration must contain `declaration.dimension == "observation_role"`
and an `ObservationRoleReference` whose exact code is `measured_actual` in the
project-local system and accepted model edition.

Command/target, estimate/inferred, calculated/derived, cumulative amount,
instantaneous rate, storage, configuration, and aggregate roles are rejected
by FM-001. VSP, quantity-kind, model unit, conversion, and dimensional
algebra are not FM admission requirements and are independent future FA
prerequisites.

The immutable orientation literal order is:

1. `aligned`;
2. `opposite`;
3. `unsigned_magnitude`;
4. `not_applicable`.

Orientation never reverses FRG direction. FM reads, calculates, converts,
normalizes, or evaluates no numeric sign. Zero, negative values, bidirectional
physical behavior, and unit conversion are future evaluator concerns. There is
no positive `unknown` orientation; absence or uncertainty is a query status.

## 13. Exact same-ledger support matrix

Every positive FM record must pin exact records in the same selected model
revision, with these exact relationships:

```text
FRG  flow_registration_record_id              -> flow_anchor_id
VRG  variable_registration_record_id          -> variable_anchor_id
PRG  port_registration_record_id              -> participant_port_anchor_id
FLD  flow_declaration_record_id               -> flow_anchor_id/context/port support
VPA  variable_port_association_record_id      -> variable_anchor_id/port/context
VSM  variable_semantic_declaration_record_id  -> variable_anchor_id/observation_role/measured_actual
```

The FRG must contain the participant port in exactly one derived source/sink
set. The FLD must have the exact context and its source or sink direction pins
must include the participant port. The VPA must have the exact variable,
participant port, and context. The VSM must have the exact variable and the
measured-actual observation-role reference (`project_local` /
`ohk-observation-roles-1` / `measured_actual`). VSM is context-independent;
only FLD and VPA must match the exact FMA assertion context.

The FM record does not duplicate FLD PCN/PIF pins. It does not cite
source-interpretation, semantic-compatibility, EA, evidence-alignment, TA,
temporal, observation, or sibling-ledger objects as model support. Its own
non-empty evidence tuple uses the existing citable evidence grammar; every
model-record evidence reference must be one of the six positive support
records or another accepted citable model record required by the repository's
uniform closure rule. FM withdrawal is never in that tuple.

Support records must exist, be structurally exact, reference-closed, and belong
to the selected membership at append/load time. They need not be current:
superseded, withdrawn, conflicted, inactive, absent from another historical
revision, or unaligned support is disclosed by queries and never retargeted.

## 14. Correction DAG, conflict, and withdrawal

All `supersedes` parents must be membership-present positive `fma_` records
with the exact same immutable subject and the same derived root. The root is
the parentless record's record ID and is carried by indexes, not serialized as
an authority field.

Allowed:

- a parentless root;
- one or more same-root parents;
- complete same-root convergence to one effective body;
- independent parentless roots with identical effective bodies, disclosed as
  corroborating roots.

Rejected:

- foreign parents or cross-root parents;
- partial cross-root repair or cross-root convergence;
- cycles, self-supersession, duplicate parents, missing parents;
- a successor of a withdrawn parent;
- duplicate record IDs/files and invalid ancestry; independent parentless roots
  for one subject are allowed and may corroborate or disagree.

Same-root multiple current tips are `conflicted`. Independent roots with
different effective bodies are explicit `cross_root_effective_body_disagreement`.
No timestamp, authority, ID, filename, or append order selects a winner.

The exact withdrawal rules are:

- `withdraws` identifies exactly one current eligible positive tip in the
  selected membership;
- unknown, foreign, superseded, already-withdrawn, or non-tip targets reject;
- sibling fork tips may be selectively withdrawn;
- withdrawal is itself indexed for activity but is not a parent and cannot be
  cited as evidence;
- selected-membership activity for the target becomes `withdrawn`;
- replay of a membership without the withdrawal may revive the earlier tip.

## 15. Canonical, store, revision, and index integration

Prospective append validation occurs in this exact order, with no file written
until every step succeeds:

1. validate all pre-existing records unchanged;
2. validate the FM positive or withdrawal contract and content-derived ID;
3. prove FRG/VRG/PRG registration and selected-revision membership;
4. prove participant membership in FRG and derive source/sink role;
5. prove exact-context FLD/VPA and measured-actual VSM support;
6. validate evidence closure and withdrawal uncitability;
7. validate subject, root, parent, cycle, convergence, and withdrawal rules;
8. derive tips, activity, effective bodies, conflicts, and support relations;
9. build immutable subject, flow, variable, port, context, root, and record-ID
   indexes;
10. publish the complete validated revision only after all preceding steps.

The `ModelRecord` union, model-record ID pattern, canonical record dispatch,
store bucket dispatch, file grammar, and accepted public exports gain exactly
the two classes and two record kinds in Sections 8–9. Existing records,
fields, IDs, hashes, and revision bytes do not change. `ModelRevision` remains
the sorted explicit membership, never a directory enumeration.

## 16. Exact query names and inputs

The exact five public `ModelQueries` methods are:

1. `flow_measurement_association(flow_anchor_id, variable_anchor_id, participant_port_anchor_id, context, orientation) -> FlowMeasurementAssociationResult`;
2. `flow_measurement_associations_for_flow(flow_anchor_id, *, context) -> FlowMeasurementAssociationsForFlowResult`;
3. `flow_measurement_associations_for_variable(variable_anchor_id, *, context) -> FlowMeasurementAssociationsForVariableResult`;
4. `flow_measurement_associations_at_port(participant_port_anchor_id, *, context) -> FlowMeasurementAssociationsAtPortResult`;
5. `flow_measurement_assertion(record_id) -> FlowMeasurementAssertionResult`.

The exact lookup includes every immutable subject dimension, including
orientation. The implicit `direct_measurement_relevance` dimension has only
the v1 admitted value and is therefore not a caller-supplied parameter; the
lookup still selects the complete v1 subject. Each reverse lookup has its own immutable index and exact context;
none is an alias or unbounded scan. The five methods accept only validated
public identifiers/context and injected loaded model material through the
existing `ModelQueries` object. They perform no store access, write, clock
read, environment lookup, evidence selection, observation read, EA call, or
TA call.

## 17. Exact result classes, axes, and exports

The exact public Slice B type aliases, in literal order, are:

```text
FlowMeasurementEndpointRegistration = Literal[
  "all_registered", "flow_not_registered", "variable_not_registered",
  "port_not_registered", "multiple_not_registered"]
FlowMeasurementReverseRegistration = Literal[
  "not_registered", "registered"]
FlowMeasurementDeclarationPresence = Literal["not_declared", "declared"]
FlowMeasurementDeclarationConclusion = Literal[
  "not_evaluated", "declared_direct_measurement_relevance", "conflicted",
  "inactive"]
FlowMeasurementSupportKind = Literal[
  "frg", "vrg", "prg", "fld", "vpa", "vsm"]
FlowMeasurementSupportActivity = Literal[
  "permanent", "current", "superseded", "withdrawn"]
FlowMeasurementSupportLineageHealth = Literal[
  "not_applicable", "healthy", "conflicted", "inactive"]
FlowMeasurementSupportAlignment = Literal["exact", "unaligned"]
FlowMeasurementOrientation = Literal[
  "aligned", "opposite", "unsigned_magnitude", "not_applicable"]
FlowMeasurementAgreementFinding = Literal[
  "one_healthy_root", "corroborating_healthy_roots",
  "same_root_conflict", "inactive_roots_present",
  "cross_root_effective_body_disagreement"]
FlowMeasurementAssertionLookupStatus = Literal["not_found", "found"]
```

The existing public `AssertionActivity`, `ContainingLineageHealth`, and
`FlowPortRole` aliases are reused where their semantics are exact. They are
not re-exported under FM-specific duplicate names. There is no support-
presence alias: a support row exists only for one of the six mandatory pins.
There is no separate semantic-support alias because the VSM row already
discloses activity, health, and current alignment. There is no positive
`unknown` or result-only orientation token; optional outer fields use explicit
`None` when no positive assertion selects an orientation or role.

The required nested public rows, with exact field order, are:

```text
FlowMeasurementSupportRow:
  support_kind: FlowMeasurementSupportKind
  record_index: StrictInt >= 0
  activity: FlowMeasurementSupportActivity
  containing_lineage_health: FlowMeasurementSupportLineageHealth
  current_alignment: FlowMeasurementSupportAlignment

FlowMeasurementEffectiveBodyGroupRow:
  group_index: StrictInt >= 0
  representative_current_tip_index: StrictInt >= 0
  current_tip_indices: tuple[StrictInt >= 0, ...]
  participating_root_indices: tuple[StrictInt >= 0, ...]
  participant_role: FlowPortRole
  orientation: FlowMeasurementOrientation
  support_rows: tuple[FlowMeasurementSupportRow, ...]

FlowMeasurementRootRow:
  root_index: StrictInt >= 0
  root_record_index: StrictInt >= 0
  lineage_record_indices: tuple[StrictInt >= 0, ...]
  current_tip_indices: tuple[StrictInt >= 0, ...]
  withdrawal_indices: tuple[StrictInt >= 0, ...]
  lineage_health: ContainingLineageHealth
  effective_body_group_indices: tuple[StrictInt >= 0, ...]

FlowMeasurementEntryRow:
  entry_index: StrictInt >= 0
  flow_anchor_id: str matching FLOW_ANCHOR_ID_PATTERN
  variable_anchor_id: str matching VARIABLE_ANCHOR_ID_PATTERN
  participant_port_anchor_id: str matching PORT_ANCHOR_ID_PATTERN
  orientation: FlowMeasurementOrientation
  declaration_conclusion: FlowMeasurementDeclarationConclusion
  agreement_findings: tuple[FlowMeasurementAgreementFinding, ...]
  participant_role: FlowPortRole
  roots: tuple[FlowMeasurementRootRow, ...]
  effective_body_groups: tuple[FlowMeasurementEffectiveBodyGroupRow, ...]
  current_assertion_indices: tuple[StrictInt >= 0, ...]
```

All nested fields are required; there are no omitted defaults. Every empty
tuple must be serialized explicitly. Material indices are non-boolean,
nonnegative, unique where plural, in range, and strictly increasing by the
selected material's record-ID order. `root_index`, `group_index`, and
`entry_index` are likewise non-boolean, contiguous from zero, and refer only
to their containing tuple. Root rows are ordered by root record ID.

An effective-body group contains only current tips with one identical private
canonical Section 10 body. Groups are ordered by those canonical body bytes;
the representative is the lowest-record-ID current tip in the group. A root
with tips in two bodies points to two group indices and no row selects one of
them. A group may contain tips from several roots, and one conflicted root may
participate in several groups. Inactive roots have no current tips and an
empty group-index tuple.

Every effective-body group and every found positive assertion disclosure has
exactly six support rows ordered `frg`, `vrg`, `prg`, `fld`, `vpa`, `vsm`.
There are no support rows on roots, absent results, reverse-result emptiness,
not-found assertion results, or withdrawal disclosures. Reverse entries carry
one complete immutable subject in the outer result's exact context. They do
not repeat material or context.

The five outer public result classes and exact field order are:

```text
FlowMeasurementAssociationResult:
  material: ModelQueryMaterial
  flow_anchor_id: str matching FLOW_ANCHOR_ID_PATTERN
  variable_anchor_id: str matching VARIABLE_ANCHOR_ID_PATTERN
  participant_port_anchor_id: str matching PORT_ANCHOR_ID_PATTERN
  context: AssertionContext
  orientation: FlowMeasurementOrientation
  endpoint_registration: FlowMeasurementEndpointRegistration
  declaration_presence: FlowMeasurementDeclarationPresence
  declaration_conclusion: FlowMeasurementDeclarationConclusion
  agreement_findings: tuple[FlowMeasurementAgreementFinding, ...]
  participant_role: FlowPortRole | None
  roots: tuple[FlowMeasurementRootRow, ...]
  effective_body_groups: tuple[FlowMeasurementEffectiveBodyGroupRow, ...]
  current_assertion_indices: tuple[StrictInt >= 0, ...]

FlowMeasurementAssociationsForFlowResult:
  material: ModelQueryMaterial
  flow_anchor_id: str matching FLOW_ANCHOR_ID_PATTERN
  context: AssertionContext
  registration_status: FlowMeasurementReverseRegistration
  declaration_presence: FlowMeasurementDeclarationPresence
  entries: tuple[FlowMeasurementEntryRow, ...]

FlowMeasurementAssociationsForVariableResult:
  material: ModelQueryMaterial
  variable_anchor_id: str matching VARIABLE_ANCHOR_ID_PATTERN
  context: AssertionContext
  registration_status: FlowMeasurementReverseRegistration
  declaration_presence: FlowMeasurementDeclarationPresence
  entries: tuple[FlowMeasurementEntryRow, ...]

FlowMeasurementAssociationsAtPortResult:
  material: ModelQueryMaterial
  participant_port_anchor_id: str matching PORT_ANCHOR_ID_PATTERN
  context: AssertionContext
  registration_status: FlowMeasurementReverseRegistration
  declaration_presence: FlowMeasurementDeclarationPresence
  entries: tuple[FlowMeasurementEntryRow, ...]

FlowMeasurementAssertionResult:
  material: ModelQueryMaterial
  record_id: str matching ^(?:fma|fmw)_[0-9a-f]{64}$
  lookup_status: FlowMeasurementAssertionLookupStatus
  record_index: StrictInt >= 0 | None
  assertion_activity: AssertionActivity | None
  containing_root_health: ContainingLineageHealth | None
  containing_subject_conclusion: FlowMeasurementDeclarationConclusion | None
  containing_agreement_findings: tuple[FlowMeasurementAgreementFinding, ...] | None
  root_record_index: StrictInt >= 0 | None
  successor_indices: tuple[StrictInt >= 0, ...]
  withdrawal_indices: tuple[StrictInt >= 0, ...]
  participant_role: FlowPortRole | None
  orientation: FlowMeasurementOrientation | None
  support_rows: tuple[FlowMeasurementSupportRow, ...]
```

Every listed outer field is required; empty tuples and `None` values must be
serialized explicitly and cannot be supplied by omission. Each outer result
carries one complete `ModelQueryMaterial` exactly once. Nested rows never
carry material, records, or duplicate record IDs.

For an exact lookup with any unregistered endpoint or no matching subject,
`declaration_presence` is `not_declared`, `declaration_conclusion` is
`not_evaluated`, `agreement_findings`, `roots`, `effective_body_groups`, and
`current_assertion_indices` are empty, and `participant_role` is `None`.
`endpoint_registration` independently states which endpoint registration is
absent. If all endpoints are registered but the port is not a participant in
that flow, the result is the same structured no-declaration shape with
`all_registered`; registration does not manufacture FM relevance.

For each reverse result, an unregistered selected endpoint uses
`registration_status == "not_registered"`, `declaration_presence ==
"not_declared"`, and an empty entry tuple. A registered endpoint with no FM
subject in the exact context uses `registered`, `not_declared`, and an empty
entry tuple. A non-empty entry tuple requires `registered` and `declared`.
Cross-context entries never appear.

The reverse methods use only these accepted immutable indexes:

- flow: `flow_measurement_ids_by_flow_context[(flow_anchor_id, context)]`;
- variable: `flow_measurement_ids_by_variable_context[(variable_anchor_id, context)]`;
- port: `flow_measurement_ids_by_port_context[(participant_port_anchor_id, context)]`.

Each selected record ID is grouped by the complete Section 10 subject; one
subject becomes one entry regardless of its root count. Flow entries order by
`(variable_anchor_id, participant_port_anchor_id, orientation_rank)`, variable
entries by `(flow_anchor_id, participant_port_anchor_id, orientation_rank)`,
and port entries by `(flow_anchor_id, variable_anchor_id, orientation_rank)`.
`orientation_rank` is the Section 12 literal position, never lexicographic or
caller-defined. Entry indices are assigned only after semantic sorting.
Duplicate subjects reject reconstruction; no reverse method aliases another,
scans unbounded records, or emits one entry per root or assertion.

`FlowMeasurementAssertionResult` accepts only syntactically valid `fma_` or
`fmw_` IDs. A missing ID uses `not_found`, null optional fields, and empty
index/support tuples. A found withdrawal carries only its `record_index`; the
withdrawal record at that index contains its target, while every positive-only
field remains null/empty. A found positive carries its activity, containing
root health and subject conclusion/findings, root/successor/withdrawal
indices, derived role, orientation, and exactly six support rows for that
selected assertion body.

The subject conclusion has exact precedence. With no matching FMA it is
`not_evaluated`. With declarations, any same-root conflict or cross-root body-
set disagreement yields `conflicted`. Otherwise any healthy active root yields
`declared_direct_measurement_relevance`, including mixtures with inactive
roots. Only an all-inactive declared subject yields `inactive`. No singular
assertion activity or lineage health is selected at subject level.

Agreement findings are retained in their literal order. `one_healthy_root`
appears when exactly one root is healthy; `corroborating_healthy_roots` appears
when at least two healthy roots participate in one body group;
`same_root_conflict` appears when any root is conflicted;
`inactive_roots_present` appears when any root is inactive; and
`cross_root_effective_body_disagreement` appears exactly when distinct active
roots have unequal current body sets. Applicable findings coexist and do not
select a winner.

Support-row reachability is exact:

| Kind | Activity | Containing lineage health | Current alignment |
|---|---|---|---|
| FRG / VRG / PRG | `permanent` only | `not_applicable` only | `exact` only |
| FLD / VPA, pinned record is a current tip | `current` | `healthy` or `conflicted` | `exact` |
| FLD / VPA, pinned record is superseded | `superseded` | `healthy`, `conflicted`, or `inactive` | `exact` while active; `unaligned` when inactive |
| FLD / VPA, pinned record is withdrawn | `withdrawn` | `healthy`, `conflicted`, or `inactive` | `exact` while another active tip remains; `unaligned` when inactive |
| VSM, pinned record is current | `current` | `healthy` or `conflicted` | `exact` when every current observation-role tip remains exact measured-actual; otherwise `unaligned` |
| VSM, pinned record is superseded | `superseded` | `healthy` or `conflicted` | `exact` when every current observation-role tip remains exact measured-actual; otherwise `unaligned` |

FLD/VPA lineage subjects preserve the exact FM-required context/participant
relation, so an active lineage remains aligned even when the pinned record is
stale. An inactive FLD/VPA lineage has no current support and is unaligned.
VSM alignment compares the complete current context-independent observation-
role tip set with the exact measured-actual token. VSM has no
`AssertionContext`, withdrawal record, `withdrawn` activity, or `inactive`
health. Every table cell has a future valid-world witness; all other kind/
activity/health/alignment products are invalid.

The accepted 205-name Slice A export prefix remains byte-order exact. Slice B
adds exactly these 20 public names in this order, producing exactly 225 total
`backend.model_kernel.__all__` names:

```text
FlowMeasurementEndpointRegistration
FlowMeasurementReverseRegistration
FlowMeasurementDeclarationPresence
FlowMeasurementDeclarationConclusion
FlowMeasurementSupportKind
FlowMeasurementSupportActivity
FlowMeasurementSupportLineageHealth
FlowMeasurementSupportAlignment
FlowMeasurementOrientation
FlowMeasurementAgreementFinding
FlowMeasurementAssertionLookupStatus
FlowMeasurementSupportRow
FlowMeasurementEffectiveBodyGroupRow
FlowMeasurementRootRow
FlowMeasurementEntryRow
FlowMeasurementAssociationResult
FlowMeasurementAssociationsForFlowResult
FlowMeasurementAssociationsForVariableResult
FlowMeasurementAssociationsAtPortResult
FlowMeasurementAssertionResult
```

This is 11 new aliases, four nested rows, and five outer results. The five
query methods are methods only and are never exported as free functions.
Private helpers remain private. No FM-specific record builder is added;
records continue to use only generic `build_record(record_cls, **fields)`.

## 18. Authoritative result reconstruction

Every outer result reconstructs the supplied material from plain serialized
values through existing model-kernel revalidation. It proves every referenced
record belongs to the selected revision, recomputes record IDs, revision ID,
registration status, subject matches, FRG-derived role, FLD/VPA/VSM exact
support, roots, parents, tips, body groups, corroboration/disagreement,
withdrawal activity, support activity/health/current alignment, conclusions,
findings, indices, counts, and deterministic ordering. It derives each
reverse entry from exactly one subject selected through the existing
flow/context, variable/context, or port/context FM index, then uses the same
private subject-payload builder as the exact lookup. Revalidation never calls
a public query recursively and never silently reselects material.

It rejects forged Pydantic instances, `model_construct`, `model_copy`, hidden
or private state, scalar subclasses, booleans as indices, wrong union arms,
stale derived values, missing/duplicate/extra/reordered/substituted rows,
cross-context leakage, revision/material substitution, cycles, and oversized
graphs using accepted model-kernel limits. It performs no store, filesystem,
network, clock, environment, cache, or write operation.

Result validation uses the existing `ModelQueryMaterial` reconstruction and
`validate_record_collection` authority; FM adds no second graph-validation
system. Only after material reconstruction succeeds may private builders
derive rows. Individual assertion activity, containing-root health, support
activity, support-lineage health, and current alignment remain distinct.
Stale or unaligned support is disclosure, not physical invalidity. A 36-record
pre-FM revision returns structured absence with exactly its original material.

## 19. Import and isolation direction

The only permitted production direction is:

```text
system_identity
      ^
model_kernel  (FM declarations, indexes, and queries)
      ^
future pure FA-001 composition
```

`model_kernel` must not import data sources, temporal state, identity-binding
stores, evidence assurance/alignment, model state, source interpretation,
semantic compatibility, constraint evaluation, behavior evaluation, state
classification, transition assessment, CAD/PDF adapters, connectors, or UI.
FM imports only accepted kernel contracts, canonical/store/query facilities,
Pydantic, and the standard library.

## 20. Historical replay and structured absence

Every explicit pre-FM membership returns structured absence from each relevant
query. The current 36-record revision remains byte-identical, contains no FM
record, and receives no synthetic association or demonstration.

A future FM membership must include exact same-revision dependency closure and
an explicit sorted record-ID list. Replay derives currentness, conflict,
withdrawal, body grouping, and support disclosure from that selected material.
Filesystem enumeration, filenames, timestamps, authority, and append order
never select a winner. Historical bytes and support pins are not retargeted.

## 21. Threat model

The implementation must refuse or disclose:

- command, estimate, derived, rate, amount, aggregate, or storage role;
- orientation drift, participant substitution, non-FRG port, wrong flow, or
  forged source/sink body field;
- FLD/VPA context or subject substitution, or VSM variable, dimension,
  system, edition, code, revision, ID, or other support substitution;
- duplicated PCN/PIF pins, sibling-ledger citations, upper-result citations,
  citable withdrawals, or evidence-free positive records;
- foreign/cross-root/partial parents, cycles, self-parent, duplicate parents,
  successor of withdrawn parent, and invalid withdrawal target;
- different support pins hidden as one effective body;
- independent identical roots treated as conflict rather than corroboration;
- timestamps, authority, IDs, filenames, or order selecting winners;
- cross-context lookup leakage and forged carry-once material;
- no-I/O violations, hostile graph/scalar/index input, or automatic model
  truth from observations, EA, or TA;
- presentation of an association as measurement, rate, active flow,
  occurrence, conservation, correctness, or safety.

## 22. Corrected adversarial acceptance matrix

Original FM-A01–FM-A28 remain stable and are corrected as follows:

| ID | Normative witness |
|---|---|
| FM-A01 | `fma_`/`fmw_` IDs, record kinds, canonical bytes, and prefix collision checks are exact. |
| FM-A02 | The six immutable subject dimensions reject any in-lineage drift. |
| FM-A03 | Exact FRG/VRG/PRG/FLD/VPA/VSM closure is required in one revision. |
| FM-A04 | VPA, names, units, ownership, topology, and PIF direction cannot create FM. |
| FM-A05 | Non-FRG and wrong-role ports refuse; source/sink is derived, never caller-supplied. |
| FM-A06 | Only direct measured-actual relevance is admitted; every other value role refuses. |
| FM-A07 | Orientation literals are exact, immutable, ordered, and never numerically evaluated. |
| FM-A08 | Fan-in/fan-out and no aggregate locus cannot create branches, balance, or conservation. |
| FM-A09 | Same-root correction, fork, convergence, conflict, and corroboration follow the fixed DAG. |
| FM-A10 | Withdrawal has no evidence and targets only one eligible current tip. |
| FM-A11 | Historical replay revives explicit prior membership and never chooses by time/rank/order. |
| FM-A12 | Later support supersession/withdrawal/conflict is disclosed without retargeting bytes. |
| FM-A13 | Exact lookup includes flow, variable, port, context, the fixed implicit v1 relation, and orientation. |
| FM-A14 | Three reverse indexes are non-overlapping, exact-context, deterministic, and bounded; assertion lookup is separate. |
| FM-A15 | Results distinguish registration, declaration conclusion, per-root lineage, assertion activity, support activity, support health, current alignment, role, orientation, and agreement axes. |
| FM-A16 | Pre-FM 36-record material returns structured absence. |
| FM-A17 | One complete material object is carried once in each result. |
| FM-A18 | Forged nested models, wrong unions, hidden state, stale fields, indices, rows, cycles, and substitutions reject. |
| FM-A19 | Query/result validation is no-I/O and no-write. |
| FM-A20 | Canonical bytes/order are stable across hash seeds and construction order. |
| FM-A21 | Kernel import isolation excludes every upper/sibling package. |
| FM-A22 | Every public field, literal, export, refusal, and carry-once rule is exact. |
| FM-A23 | No association result uses observation, measured, flowing, occurrence, conservation, correctness, or safety language. |
| FM-A24 | Observation/EA/TA cannot append or mutate model truth. |
| FM-A25 | Existing records, IDs, revisions, disclosures, and bytes remain unchanged. |
| FM-A26 | Any append/demo is separately gated and absent from FM v1. |
| FM-A27 | Future FA-001 must consume explicit FM facts rather than infer relevance; FM makes no promise that FA will be implemented. |
| FM-A28 | Occurrence/history remains absent without later time-window, continuity, and authenticity contracts. |
| FM-A29 | Direct-measurement-to-command/estimate/derived mutation within one lineage rejects. |
| FM-A30 | Participant-port mutation with retained parents rejects as a new-subject violation. |
| FM-A31 | Aggregate/null/whole-flow/storage/control-volume locus rejects before append. |
| FM-A32 | Citable/evidence-bearing withdrawal rejects the withdrawal contract and evidence union. |
| FM-A33 | Duplicate, foreign, cross-root, partial, cyclic, self, and withdrawn-parent ancestry rejects. |
| FM-A34 | Different support pins produce different effective bodies. |
| FM-A35 | Exact measured-actual VSM variable/dimension/system/edition/code/revision/ID substitution rejects; VSM has no context. |
| FM-A36 | Cross-context query input cannot leak a declaration or support row. |
| FM-A37 | Independent identical roots corroborate; independent different bodies disagree. |
| FM-A38 | Result replacement and material replacement are detected by authoritative reconstruction. |
| FM-A39 | Boolean indices, hostile scalar subclasses, oversized/deep/cyclic graphs reject before lower work. |
| FM-A40 | Exact deterministic reproduction covers alternate construction order and hash seeds. |
| FM-A41 | One conflicted root with current tips in multiple bodies points to every applicable body group and selects no body/support set. |
| FM-A42 | Independent healthy roots in one effective-body group disclose ordered corroboration without selecting a representative root as authority. |
| FM-A43 | Independent active roots with unequal body sets retain every group/root and disclose cross-root disagreement without a winner. |
| FM-A44 | Healthy-plus-conflicted mixtures retain both findings and produce aggregate `conflicted` precedence. |
| FM-A45 | Healthy-plus-inactive mixtures retain both findings and remain positively declared because a healthy active root exists. |
| FM-A46 | Conflicted roots with equal body sets do not manufacture cross-root disagreement; unequal sets do. |
| FM-A47 | All-inactive roots retain their lineage rows, have no active body groups, and produce aggregate `inactive`. |
| FM-A48 | All four orientations produce separate exact/reverse entries and exact/assertion agreement in literal order. |
| FM-A49 | Every reachable FRG/VRG/PRG/FLD/VPA/VSM activity-health-alignment combination has a valid-world witness. |
| FM-A50 | Impossible registration lifecycle states and contextual/withdrawn/inactive VSM states reject reconstruction. |
| FM-A51 | Exact, flow reverse, variable reverse, port reverse, and assertion results agree through one shared subject payload. |
| FM-A52 | Exact-context filtering excludes every otherwise matching cross-context subject from all three reverse indexes. |
| FM-A53 | Unregistered, registered-but-empty, no-declaration, positive, not-found, and withdrawal shapes have exact null/empty cardinality. |
| FM-A54 | Missing, duplicate, extra, reordered, Boolean, negative, out-of-range, or substituted rows and indices reject. |
| FM-A55 | Forged material, revision, record ID, nested instance, hidden state, wrong union, cycle, and stale derived value reject before disclosure. |
| FM-A56 | Each outer result carries material once; nested rows are index-only and validation performs no I/O or writes. |
| FM-A57 | The accepted 36-record pre-FM membership returns structured absence from all five queries with exact unchanged material. |
| FM-A58 | Public tests pin all 20 Slice B additions, 225 total exports, every field in order, and every literal in order using equality, never subsets. |

Every public literal and refusal is reached by a valid disposable world or is
identified as structurally impossible by the exact contract. Tests assert full
field sets and literal order, never subsets.

## 23. Deterministic verification strategy

Verification must cover exact record IDs, JSON canonical bytes, file buckets,
dispatch, evidence citability, append atomicity, replay, indexes, builders,
exports, and all five queries. It must use at least five hash seeds and
independent construction order.

Hostile tests must use plain reconstructed values, forged model instances,
`model_construct`, `model_copy`, hidden/private state, wrong union arms,
cycles, stale derived fields, booleans, scalar subclasses, missing/duplicate/
reordered indices, cross-context rows, and revision substitution. No-I/O
spies must cover filesystem, socket, SQLite, environment, clocks, connectors,
EA, TA, and writes.

The 36-record material must be replayed before and after all disposable FM
worlds. Existing lower digests, revision, ledger, disclosures, memberships,
and settings must remain exact. No full repository or clean-checkout result is
claimed until an implementation slice runs it.

## 24. Two owner-gated implementation slices

### Slice A — declaration and ledger integrity

Slice A is owner accepted at exact tested implementation
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`. Its authorized scope added only
`FlowMeasurementAssociation`,
`FlowMeasurementAssociationWithdrawal`, exact canonical/store/evidence/DAG
validation, prefix/union dispatch, immutable indexes, replay, builders,
exports, and hostile integrity tests. It implemented the ten-step append order
in Section 15, preserved all existing records and bytes, and prepared the
immutable indexes needed by Slice B.

Slice A must not implement the five public query methods beyond construction
needs, append a fixture, create a demo, call evidence or temporal stores, or
add an upper composition layer.

### Slice B — queries and authoritative results

The corrected contract permits Slice B to add exactly the five methods, 11
aliases, four nested rows, and five outer result classes in Section 17, exact
orthogonal statuses, deterministic indexed ordering, carry-once material,
authoritative reconstruction, adversarial hardening, import isolation, and
full verification. Implementation remains unauthorized until the owner
accepts this exact correction and separately authorizes Slice B.

The future execution sequence and exact FM-B01–FM-B58 executable obligations
are recorded in
`docs/superpowers/plans/2026-09-09-fm001-slice-b-implementation-plan.md` and
`docs/superpowers/plans/2026-09-09-fm001-slice-b-adversarial-acceptance-matrix.md`.
Those documents are plans, not implementation authorization.

There is no Slice C and no demonstration slice. Any later rehearsal, fixture,
identity mint, append, or authoritative artifact requires a separate owner
proposal and authorization.

## 25. Exclusions, future FA boundary, and implementation readiness

FM-001 excludes command/target, estimate, inferred, calculated, derived,
cumulative, rate, storage, aggregate, whole-flow, value evaluation, sign
normalization, unit conversion, dimensional algebra, arithmetic, aggregation,
balance, conservation, evidence selection/alignment, temporal queries,
observed/active flow, occurrence/history, continuity, sensor/channel/device or
physical-boundary identity, FA-001, facades, UI, connectors, CAD/PDF,
configuration, causal, diagnostic, impact, action, goal, planning, safety,
recommendation, and all TA-001 changes.

Future FA-001 may consume carried FM results, FL declaration/support, model
semantic/value compatibility, and independently selected/aligned evidence. It
must separately decide time, numeric, unit/conversion, aggregation, coverage,
and refusal policies. FM-001 is not sufficient for FA-001 and makes no promise
that FA-001 will be implemented.

The corrected Slice B contract is implementation-ready: names, prefixes,
record kinds, IDs, fields, immutable subject/body keys, support matrix,
lifecycle, withdrawal, validation order, indexes, queries, result axes,
exports, import boundary, replay, limits, hostile requirements, slices, and
exclusions are frozen.
There are zero unresolved semantic questions. The sole owner gate is approval
of this exact Slice B public-contract correction and separate authorization to
implement it. ADR-0021 exists and is amended to reference these corrected
bytes.

END OF FM-001 CORRECTED FINAL SYNTHESIS
