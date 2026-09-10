# DI-001 — Explicit Declaration Dependency and Change-Impact Disclosure

Codex lead design proposal — 2026-09-10. Design-only; not owner approved.

## 1. Recommendation and strongest honest answer

**Recommend outcome 1: no new milestone—existing public APIs suffice** for a
bounded, explicitly scoped engineering change review. Use application-owned
composition of complete before/proposed model material, existing owning queries,
and an independently nominated decision inventory. No implementation is
recommended in this proposal: no additive kernel query, sibling `model_impact`,
shared runtime function, durable dependency record, identity or ADR.

The named consumer is the **engineering change review and
configuration-management workflow**. Its strongest answer is:

> For these complete, independently specified before and proposed memberships,
> which retained declarations have changed explicit support/currentness or
> applicability, and which of this named, complete decision-review set require
> reevaluation, with every relevant typed reference and selection-dependency
> path disclosed under a bounded review scope?

This does not discover every decision ever made by every application. The
repository has no authoritative inventory of those decisions or their hidden
application dependencies. The caller must nominate that set and its completeness
authority; otherwise the answer for unlisted decisions is `unknown`, not
`unaffected`. A new graph API cannot manufacture that missing application fact.

No concrete substitution, omission, closure or reproducibility failure was found
that the existing full-material validation and explicit public joins cannot
prevent within this scope. There is no newly answerable backend question: the
design makes an existing composition precise. Efficiently packaging it is not
an independent integrity requirement. The original broad question must not be
answered with a false global completeness claim.

Physical, causal, operational, safety, cost, schedule and failure impact are
excluded. A reachable citation is not causality; a stale support pin is not a
prediction that behavior changed; a request for reevaluation does not reverse
the old verdict.

## 2. Verified live baseline and protected digests

All checks below were performed before writing this file. No fetch was needed;
the live local remote-tracking ref was inspected after the completed push.

| Checkpoint | Observed value |
| --- | --- |
| Branch | `main` |
| HEAD = origin/main | `181f5c8484ce31b7f4ef377e4af2399ed946dfa0` |
| Latest commit | `docs: close CS-001 as application policy` |
| Working tree | Clean initially; no uncommitted tracked changes |
| Reconciliation / CS status | Post-FC reconciliation owner accepted; CS-001 closed without implementation as application policy, not deferred architecture |
| Authoritative model | 36 records; `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| Model-kernel exports | 236 unique ordered names |
| FCD/FCW; FMA/FMW | `0/0`; `0/0` |
| ADRs | 22 accepted, contiguous and unique, ADR-0001 through ADR-0022 |
| ADR-0023 | Absent and unallocated; not reserved by DI-001 |

These full digests were recomputed from the repository, not completed from
abbreviated receipts:

| Protected artifact | SHA-256 |
| --- | --- |
| [Accepted reconciliation](../reports/2026-09-10-post-fc001-architecture-and-adr-reconciliation-report.md) | `9593532154632d7cabac8e67db3c0a63d22f677858a973bb26cec14b83a06dd5` |
| [CS owner decision](../reports/2026-09-10-cs001-application-policy-owner-decision.md) | `8557f2252c226b43dabc17ae4ffc5b8a529ac3d26999a456495e6b21c2ad33e3` |
| [CS correction report](../reports/2026-09-10-cs001-proposal-correction-report.md) | `b28c775071c0ef4aaa4af9a4593f8c31d76b756d811a3ce4ab40b3377e8517e5` |
| [CS challenger audit](../reports/2026-09-10-cs001-codex-lead-proposal-challenger-audit.md) | `ebbe452695019d6f83a3a775149c8370125110c58461380f38a39e1092f37859` |
| [Corrected CS proposal](2026-09-10-cs001-codex-lead-proposal.md) | `ab816af9a96aa0578b29cd8209e3e0f1530ac8a02dac455a5538b58d460372c1` |
| [FC final acceptance](../reports/2026-09-09-fc001-final-owner-acceptance.md) | `1436b12aff7ad6b387a58bba0ea7d87386fffd14c151d5ad76b06384a7529ca8` |
| [FC final verification](../reports/2026-09-09-fc001-slice-b-final-verification-report.md) | `eb67c0830ac54c3caac9a8763afd0e84484edc8f7f900fd6391f137d5a9eec71` |
| Ordered compact-JSON model-kernel export list | `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252` |

Protected tree digests use a sorted repository-relative-path to file-SHA-256
mapping, encoded as compact sorted-key JSON plus one newline. All six also
matched the accepted reconciliation's protected inventories.

| Tree | Files | Inventory SHA-256 |
| --- | ---: | --- |
| `models/demo-printer` | 37 | `ea13596e56d00c1bc39866d8ddc7a0ae551af3fa2d1e3b5f500c0edec0b1ca37` |
| `bindings/demo-printer` | 6 | `11ccbed0d42505fa33925ef9ef3d56da12484f9f167106f28f3b6772c39e15b0` |
| `bindings/demo-printer-model` | 5 | `1c861155fbd04676f2ac2f86edc60f0d07899a8b1832772af9d20fb8259771dd` |
| `interpretations/demo-printer` | 3 | `819a21911a227c1175d6a5552ba924806e1ee0d13ae75009c4b789db979c83fd` |
| `showcases/demo-printer` | 9 | `dd7d8c986d769dcec519b7422cad417d6c3cdd39252dcd686c8c2a4a225d45ce` |
| `var/raw_store` (ignored) | 5 | `16ff9454f9e13cbbcb5be687d0fcbc029d80c556bd51728c6ef025f78e71d91a` |

No baseline discrepancy was found. The historical full-suite accounting remains
4,074 passing tests as recorded by FC acceptance; no new full-suite or
clean-checkout matrix is claimed for this design.

## 3. Necessity test: live public authority versus convenience

### 3.1 Existing public construction is sufficient

`backend.model_kernel.ModelQueryMaterial` carries `revision` and the complete
ordered `records` tuple. Its validator checks exact membership, canonical IDs,
all record/identity closure and correction/withdrawal invariants; `.loaded()`
reconstructs the validated `LoadedModel` and its indexes without store access.
`ModelQueries(material.loaded())` rederives existing declaration results for
that exact membership. A proposed membership need not be appended to any store
to use this path. The in-memory experiments in section 9 exercised it with
filesystem opening forbidden.

`ModelRevision` independently validates its count, sorted unique IDs and digest.
Its accepted algorithm is `"mrv_" + sha256("\n".join([model_id, *sorted_ids]))`
over UTF-8, with no trailing newline. This is documented in the
[MK design](../specs/2026-08-08-mk001-model-kernel-design.md) and implemented in
the live canonical module. A caller may construct this public value from its
explicit candidate membership; no private revision builder is required.
For the empty membership the hash input is just `model_id`.

`validate_record_collection` and effective-body serialization helpers are
implementation details, despite some internal comments calling their validation
a public trust boundary. They are not supported root exports. This proposal's
consumer needs neither private imports nor trusted hand-constructed indexes.
The public `ModelQueryMaterial` route is sufficient. An arbitrary directly
constructed `LoadedModel` is not an independent integrity proof.

### 3.2 Eight dependency categories kept distinct

| Category | What already exists | What cannot be inferred |
| --- | --- | --- |
| Direct evidence citations | Typed `evidence` arms; model-record evidence has exact membership closure. | A citation is not automatically mutable semantic support; foreign citations do not prove foreign ledger contents. |
| Model-record support references | Exact typed pins in PCM, STD, TRD, FLD, FMA and FCD, reconstructible from complete material and owning query disclosures. | Pin currentness cannot be generalized across families. |
| Embedded identity/registration closure | Permanent registration maps; `VariableAnchor.entity_anchor_id`; explicit owners, participants, state conditions and transition endpoints. | Same name, token or displayed owner is not identity substitution. |
| Correction/withdrawal ancestry | Exact `supersedes`/`withdraws` fields and copied read-only successor/root/tip/withdrawal maps. | Timestamp, authority or lexicographic ID does not resolve a conflict. |
| Currentness/applicability | Public owning queries disclose current tips, lineage health, body groups, exact support and FC applicability. | Reachability alone cannot decide whether another healthy same-body root preserves the conclusion. |
| Query-result composition | Complete result fields and explicit query selectors connect CN/VS/ES, state classification, TA, EA/alignment and the FC commissioning join. | A result's selected positive row does not enumerate all candidates that could alter its selection. Full owning query scope matters. |
| Historical replay membership | `ModelRevision.record_ids`, exact `ModelQueryMaterial`; store-bound `ModelStore.replay` for already retained IDs if explicitly requested elsewhere. | Excluding later records from a replay does not delete or undo them in the ledger. |
| Application-only dependencies | Named decision requests, policy schema/version, selectors, external expected commitments and intended review inventory. | Global decision inventory, application caches, UI state and hidden policy branches cannot be discovered from kernel citations. Missing scope means `unknown`. |

All model-reference information is public as record content. Some reverse maps
are ready-made, others require a finite typed scan; no required model reference
is available only through a private index. There is no accepted generic reverse
dependency facade or DI verdict, but their absence is not missing information.

### 3.3 Relevant live code and public surfaces inspected

The inspection covered all 32 arms of the accepted `ModelRecord` union and
their nested reference fields in [contracts](../../../backend/model_kernel/contracts.py),
the actual closure/lifecycle/index construction in [store](../../../backend/model_kernel/store.py),
[queries](../../../backend/model_kernel/queries.py),
[ModelQueryMaterial](../../../backend/model_kernel/port_results.py),
[FM support](../../../backend/model_kernel/flow_measurement_results.py),
[FC reconstruction](../../../backend/model_kernel/flow_operating_criterion_results.py),
[state](../../../backend/model_kernel/state_results.py),
[transition](../../../backend/model_kernel/transition_results.py), and
[flow results](../../../backend/model_kernel/flow_results.py).

Upper/foreign inspection included [identity binding](../../../backend/identity_binding/contracts.py),
[interpretation](../../../backend/source_interpretation/contracts.py),
[CN reconstruction](../../../backend/constraint_evaluation/contracts.py),
[state classification](../../../backend/state_classification/derivation.py),
[EA](../../../backend/evidence_assurance/contracts.py),
[alignment](../../../backend/evidence_alignment/derivation.py), and
[TA](../../../backend/transition_assessment/contracts.py).
The accepted [FC join](../specs/2026-09-09-fc001-explicit-flow-operating-criterion-design.md)
and [CS closeout](../reports/2026-09-10-cs001-application-policy-owner-decision.md)
remain authoritative; DI introduces no alternative commissioning evaluator.

## 4. Candidate-change boundary and exact comparison unit

Recommend an **explicit before/proposed pair of complete model memberships**
for application review, with a separately supplied intent tag and independent
expected membership commitments. A one-record seed may identify the question,
but cannot define the proposed world or its interactions. A bounded change
set is derived from the pair; it is not an alternative to complete material.
One set without before cannot establish a change, and IDs without proposed
record bytes cannot establish closure of new material.

| Operation | Accepted meaning; mandatory guard |
| --- | --- |
| Change immutable bytes | Forbidden. Reusing an old ID with changed content is invalid, not a correction. |
| Append correction successor | Retain the predecessor; add a valid new record with the family's exact `supersedes` rules. Currentness is recomputed from membership, not `recorded_at`. |
| Append withdrawal | Retain target and withdrawal, with that family's target/cardinality rules. There is no generic withdrawal for registrations, VSP, VSM or VCN. |
| Introduce replacement identity | New canonical anchor and registration; retain old identity and declarations. New downstream declarations must explicitly name the replacement; do not retarget old bytes or treat same display name as continuity. |
| Select historical membership | Explicit `historical_comparison` mode permits a reference-closed subset of supplied retained material. It can restore ancestor currentness within that replay only. No ledger deletion or operational undo. |
| Propose hypothetical future membership | `append_candidate` mode requires before IDs to be a subset of proposed IDs, same model ID and identical bytes for shared IDs. New records need complete structural admission but are not owner-accepted engineering truth merely because they validate. |

Derive `added_ids`, `excluded_ids` and `shared_ids` in sorted canonical order.
In append mode any exclusion is a mode/integrity refusal. In historical mode
an exclusion is explicit selection, and missing closure still refuses. The
intent “replace X” is an application request, not an inferred kernel lineage
edge between unrelated registrations. Verify claimed intent against actual
fields where the model has a corresponding operation; do not mint a replacement
edge as if the model declared it.

A structurally invalid candidate is `revision_invalid` with its actual lower
admission failure retained. It is not a normal impact list over a partially
accepted revision. Invalid inputs, wrong independent commitments and exceeded
analysis budgets are separate request refusals; they do not prove the proposed
engineering membership itself invalid. Do not fabricate a valid `ModelQueryMaterial`
for an invalid candidate just to serialize an impact result.

All additions must be assessed together. A withdrawal may be legal by itself
but illegal with a successor to the same target for the stricter claim families.
Two individually harmless withdrawals of equal-body corroborating roots can
jointly remove every current witness. A union of singleton impact lists is not
the combined answer.

## 5. Field-level dependency taxonomy across all accepted model families

### 5.1 Edge semantics and consequence profiles

Every reference row below is directed **dependent record → prerequisite**.
Reverse review follows prerequisite → dependent. The table enumerates direct
edges; longer paths are compositions of those edges, never invented shortcuts.
Multiple labels/field paths on the same endpoint pair remain separate.

| Code | Edge class and exact target condition | Correction / withdrawal / replacement / conflict / absence / historical consequence |
| --- | --- | --- |
| I | Identity ownership/registration closure: exact registered canonical anchor in this membership, plus stated owner/participant consistency. | Registrations have no correction/withdrawal lifecycle. Duplicate same-anchor registration refuses. New identity does not move dependents. Missing required registration invalidates membership. Replay must retain closure. |
| E | Evidence provenance: exact positive model record must be membership-present, not necessarily current. | Correction/withdrawal leaves retained evidence citation valid; replacement does not satisfy the old ID; conflicting evidence does not itself invalidate a citing semantic body; absent target refuses closure; historical replay requires target. |
| L | Lifecycle ancestry: exact predecessor/withdrawal target of allowed kind and same family key. | Recompute tips, roots and activity; obey the family-specific rules in 5.3. Never assume all families admit the same conflict or withdrawal. Missing ancestry/target refuses; replay recomputes from selected links. |
| H | Historical typed semantic support: exact kind, identity, subject/context/body restrictions must hold on retained record. | Correction/withdrawal does not invalidate historical admission. Replacement ID does not satisfy it. Missing/wrong-kind support invalidates membership. Current effect needs the owning query-specific S predicate, not H reachability. |
| S | Selection/currentness/applicability dependency: use owning query's entire typed key, roots and exact support conditions. | Requery before/proposed complete material; may become stale, conflicted, inactive or inapplicable, or retain its conclusion. New competing roots can matter without a citation from the old result. Historical queries use historical membership. |
| X | Foreign declared reference or opaque authority/token data. | Kernel does not dereference another ledger. Changes to an external target cannot be evaluated from the kernel alone; retain disclosure and report `unknown` outside independently supplied public foreign context. |
| Q | Query composition dependency: exact carried result/input revision, selector, cutoff, ruleset and expected commitments. | Changed input/selection domain requires reevaluation before reuse for the proposed request. The historical result remains valid for its original request; no automatic verdict inversion. |

`P` below means public record field scan; `L(...)` names a field on validated
public `LoadedModel`; `R` means an owning public result also discloses the
relation. Derived indexes are accelerators, not independent authority. A field
being public does not make arbitrary string-equality scans semantically valid.

### 5.2 Direct reference inventory

| Source kind(s) | Exact field → target kind | Profile and additional condition | Existing access / transitive continuation |
| --- | --- | --- | --- |
| EntityRegistration (`reg`) | `anchor.anchor_id` defines EntityAnchor; no model prerequisite | I definition, no outbound model reference. `display_name` and `referent_kind` are attributes, not foreign graph IDs. | P; L(`registrations_by_anchor`). |
| VariableRegistration (`vrg`) | `anchor.entity_anchor_id` → EntityRegistration; `anchor.anchor_id` defines VariableAnchor | I, embedded owner must be present. | P; L(`variable_registrations_by_anchor`); continue to owner only. |
| VariableValueSpecification (`vsp`) | `variable_anchor_id` → VariableRegistration | I; current specification S uses exact variable. Unit/value-shape scalars are not record pins. | P/R `variable_value_specification`; L(`current_specification_tips_by_variable`). |
| VariableSemanticDeclaration (`vsm`) | `variable_anchor_id` → VariableRegistration | I; S selection key is variable plus `declaration.dimension`. Quantity/role reference tokens do not cite another model record. | P/R `variable_semantics`; L(`current_semantic_tips_by_variable_dimension`). |
| ConstraintRegistration (`crg`) | `variable_anchor_id` → VariableRegistration; `anchor` defines ConstraintAnchor | I; permanent exact target variable. | P; L(`constraint_registrations_by_anchor`, `constraint_anchor_ids_by_variable`); variable → owner. |
| VariableConstraintDeclaration (`vcn`) | `constraint_anchor_id` → ConstraintRegistration | I; S unique current VCN by constraint anchor; predicate and expected semantics are values, not model-record links. | P/R `constraint_declaration`; L(`current_constraint_tips_by_anchor`); CRG → VRG. |
| RelationshipTypeDefinition (`rtd`) | `supersedes` → RTD or null | L; invariant type name, directionality, hierarchy semantics, context requirement; one current tip per name. | P; L(`types`, `current_type_by_name`, `type_name_by_id`); no imaginary TypeAnchor. |
| RelationshipAssertion (`rel`) | `type_id` → RTD; `source_anchor_id`, `target_anchor_id` → EntityRegistration | H/I; exact cited type admits endpoint kinds/context/self-edge. Cited RTD need not remain current. | P/R `relationships`; L(`assertions`); hierarchy queries use explicit relation/type/view, not every relation as containment. |
| RelationshipAssertion (`rel`) | `supersedes` → REL or null | L; same source, target, context and type-name lineage. | P; L(`superseded_by`); historical type pin remains separately visible. |
| RelationshipWithdrawal (`rwd`) | `withdraws` → REL | L; target retained; REL uniquely permits multiple withdrawals and coexistence with supersession. | P; L(`withdrawals`, `withdrawn_by`). |
| PortRegistration (`prg`) | `owner_entity_anchor_id` → EntityRegistration; `anchor` defines PortAnchor | I; permanent owner. | P/R `port`, `ports_of_entity`; L(`port_anchor_ids_by_owner`). |
| PortInterfaceDeclaration (`pif`) | `port_anchor_id` → PortRegistration | I; S key port/context/`declaration.dimension`; token value is not a model-record edge. | P/R `port_interface`; L(`current_port_interface_tips_by_key`). |
| PortConnectionAssertion (`pcn`) | `endpoint_port_anchor_ids[]` → PortRegistration | I; canonical endpoint set and exact context. Connection is a declared hyperedge, not pairwise physical propagation. | P/R `connections_exact`, `connections_of_port`, `connections_containing`; L(`port_connection_ids_by_port`). |
| PortCompatibilityDeclaration (`pcm`) | `endpoint_port_anchor_ids[]` → PRG; `basis.dimensions[].citations[].port_anchor_id` → PRG; `.declaration_record_id` → PIF | I/H; exact endpoint/context/dimension pairing. S compatibility requires each cited PIF to be the unique exact current edition; equal replacement token is insufficient. | P/R `interface_compatibility`; L(`port_compatibility_citations`, `port_compatibility_ids_by_citation`); PIF → PRG. |
| PortClaimWithdrawal (`ptw`) | `withdraws` → PIF, PCN or PCM | L; exact allowed positive kind, unsuperseded target, no duplicate withdrawal. | P/R `port_assertion`; L(`port_withdrawals_by_target`) and per-family withdrawn maps. |
| VariablePortAssociation (`vpa`) | `variable_anchor_id` → VRG; `port_anchor_id` → PRG | I/H; both owners equal in this membership, context exact. No observation/evidence-locus inference. | P/R `variable_port_association`, reverse variable/port queries; L(`variable_port_association_ids_by_subject`, `_ids_by_variable_context`, `_ids_by_port_context`). |
| VariablePortAssociationWithdrawal (`vpw`) | `withdraws` → VPA | L, strict positive-claim withdrawal rules. | P/R `variable_port_assertion`; L(`variable_port_association_withdrawn_by`). |
| BehaviorRegistration (`brg`) | `participant_variable_anchor_ids[]` → VRG; `anchor` defines BehaviorAnchor | I, permanent two-variable unordered participant set and rule family; required registration evidence below. | P/R `behavior`, `behaviors_involving_variable`; L(`behavior_anchor_ids_by_variable`). |
| BehaviorRuleDeclaration (`bhd`) | `behavior_anchor_id` → BRG; `participant_semantics[].variable_anchor_id` → VRG | I/H; locks cover exact permanent participants. `.signature` is semantic value, **not an exact VSM or VSP record pin**. BH evaluation consumes separate ES/VS results. | P/R `behavior_declaration`, `behavior_assertion`; BRG → participants; Q/S rather than fabricated VSM citation. |
| BehaviorRuleWithdrawal (`bhw`) | `withdraws` → BHD | L, strict positive-claim withdrawal rules. | P/R `behavior_assertion`; L(`behavior_rule_withdrawn_by`). |
| StateRegistration (`srg`) | `subject_entity_anchor_id` → REG; `condition_constraint_anchor_ids[]` → CRG; `anchor` defines StateAnchor | I; every CRG's variable owner must equal subject; permanent condition set. | P/R `state`, `states_of_entity`; L(`state_condition_constraint_ids_by_anchor`); CRG → VRG → REG. |
| StateDeclaration (`std`) | `state_anchor_id` → SRG; `conditions[].constraint_anchor_id` → CRG; `.constraint_declaration_record_id` → VCN | I/H; exact complete permanent condition set. **Kernel state declaration can remain declared after VCN correction**; S exact-current VCN admission is enforced by state classification, not by rewriting STD validity. | P/R `state_declaration`, `state_assertion`; Q state classification; VCN → CRG. |
| StateDeclarationWithdrawal (`stw`) | `withdraws` → STD | L, strict positive-claim withdrawal rules. | P/R `state_assertion`; L(`state_declaration_withdrawn_by`). |
| TransitionRegistration (`trg`) | `subject_entity_anchor_id` → REG; `from_state_anchor_id`, `to_state_anchor_id` → SRG | I; ordered distinct endpoints have same subject; duplicate ordered subject/endpoints prohibited. | P/R `transition`, `transitions_of_entity`; L(`transition_registration_id_by_ordered_subject_endpoints`); SRG → conditions. |
| TransitionDeclaration (`trd`) | `transition_anchor_id` → TRG; `from_endpoint.state_anchor_id`, `to_endpoint.state_anchor_id` → SRG; each `.declaration_record_id` → STD | I/H; exact endpoint roles and context. S endpoint pin relation uses state conclusion and exact STD activity; upper TA also checks classifications/evidence. | P/R `transition_declaration`, `transition_assertion`; STD → exact VCN conditions. |
| TransitionDeclarationWithdrawal (`trw`) | `withdraws` → TRD | L, strict positive-claim withdrawal rules. | P/R `transition_assertion`; L(`transition_declaration_withdrawn_by`). |
| FlowRegistration (`frg`) | `source_port_anchor_ids[]`, `sink_port_anchor_ids[]` → PRG; `anchor` defines FlowAnchor | I; disjoint role sets, exact logical signature uniqueness. `flow_kind` is a token, not a hidden identity or cause. | P/R `flow`, `flows_involving_port`; L(`flow_anchor_ids_by_port`, `flow_role_by_anchor_and_port`). |
| FlowDeclaration (`fld`) | `flow_anchor_id` → FRG; `connection_assertion_record_id` → PCN; `source_direction_pins[]`, `sink_direction_pins[]`: `.port_anchor_id` → PRG, `.declaration_record_id` → PIF | I/H; exact participant union, context and admitted source/sink direction-role PIFs. S flow support exposes pinned activity/health/current direction and alignment; other FL roots do not automatically change this exact historical support. | P/R `flow_declaration`, `flow_assertion`; PCN/PIF → PRG. |
| FlowDeclarationWithdrawal (`flw`) | `withdraws` → FLD | L, strict positive-claim withdrawal rules. | P/R `flow_assertion`; L(`flow_declaration_withdrawn_by`). |
| FlowMeasurementAssociation (`fma`) | `flow_anchor_id`, `variable_anchor_id`, `participant_port_anchor_id` → FRG/VRG/PRG; `flow_registration_record_id`, `variable_registration_record_id`, `port_registration_record_id` → exact FRG/VRG/PRG | I/H; exact identity and one registered source/sink participant role, not mere shared strings. | P/R FM exact/reverse/assertion queries; L(`flow_measurement_ids_by_subject`, `_ids_by_flow_context`, `_ids_by_variable_context`, `_ids_by_port_context`). |
| FMA (continued) | `flow_declaration_record_id` → FLD; `variable_port_association_record_id` → VPA; `variable_semantic_declaration_record_id` → VSM | H; same flow/variable/port/context; VSM exact observation-role dimension and `project_local / ohk-observation-roles-1 / measured_actual`. S activity, health and semantic alignment are distinct, as detailed in 5.4. | P/R `flow_measurement_assertion`; L(`flow_measurement_effective_body_by_id`, `flow_measurement_ids_by_effective_body`); transitively FLD → PCN/PIF. |
| FlowMeasurementAssociationWithdrawal (`fmw`) | `withdraws` → FMA | L, strict positive-claim withdrawal rules; historical FCD witness remains retained. | P/R FM assertion; L(`flow_measurement_withdrawn_by`). |
| FlowOperatingCriterionDeclaration (`fcd`) | `flow_measurement_association_record_id` → FMA; `constraint_registration_record_id` → CRG; `constraint_declaration_record_id` → VCN | H: retained exact witness, same variable/constraint and expected role. S: exact FM effective body remains currently supported, healthy/agreed relevant FM roots, unique current exact VCN and typed FL/FM supports; historical witness itself need not be current. | P/R `flow_operating_criterion`, `flow_operating_criterion_assertion`; L(`flow_operating_criterion_ids_by_subject`, `_effective_body_by_id`, `_ids_by_effective_body`). |
| FlowOperatingCriterionWithdrawal (`fcw`) | `withdraws` → FCD | L, strict positive-claim withdrawal rules. | P/R FC assertion; L(`flow_operating_criterion_withdrawn_by`). |

### 5.3 Evidence and lifecycle fields shared across those families

The `evidence[]` table applies to every evidence-bearing positive family:
VSP, VSM, CRG, VCN, PRG, PIF, PCN, PCM, VPA, BRG, BHD, SRG, STD,
TRG, TRD, FRG, FLD, FMA, FCD and REL. REG/VRG/RTD and withdrawals do
not gain an invented evidence field. Every row is directly reconstructible
from public record fields; no generic evidence reverse index is required.

| Exact discriminated field | Target / condition / consequence |
| --- | --- |
| `evidence[kind=model_record].record_id` | E; any accepted citable positive model family, never a withdrawal or revision. Membership-present even if superseded/withdrawn. Do not silently substitute an equal-body record. |
| `evidence[kind=identity_binding_record].binding_set_id`, `.record_id` | X; exact foreign ANC/IBA/IBR/IBC/IBJ citation; no foreign ledger validation by kernel. |
| `evidence[kind=source_raw_record].raw_record_id`, `.payload_checksum` | X; raw payload reference, not an acquisition occurrence or model dependency. |
| `evidence[kind=temporal_occurrence].occurrence_id` | X; declared occurrence citation, not physical event truth or a model clock. |
| `evidence[kind=structural_source_locator]`: `raw_record_id`, `payload_checksum`, `extractor_name`, `extractor_version`, `extractor_config_fingerprint`, `extractor_toolchain_fingerprint`, `locator_scheme`, `locator_value` | X; exact structural source position, syntax-validated only. It creates neither source identity resolution nor model acceptance. |
| `evidence[kind=owner_declaration].statement` | Human declared basis; no edge inferred from prose. `authority`, `recorded_at`, `note`, names and semantic tokens likewise do not create record references. |

Some E references are mandatory closure companions to H/I, but are not a second
independent semantic inference: BRG must cite its VRGs; BHD its BRG; SRG its REG
and CRGs; STD its SRG/CRGs/VCNs; TRG its REG and endpoint SRGs; TRD its TRG,
endpoint SRGs and STDs; FRG its participant PRGs; FLD its FRG, PRGs, PCN and
PIFs. Those families also require owner-declaration basis. Preserve both exact
field references where present; do not count their duplication as corroboration.
FMA/FCD have typed pins and ordinary evidence closure, not a fabricated rule
requiring every typed pin also to appear in `evidence`.

Correction edges `supersedes[]` apply to VSP, VSM, VCN, PIF, PCN, PCM, VPA,
BHD, STD, TRD, FLD, FMA and FCD; RTD/REL use scalar nullable `supersedes`.
Exact target kind matches the source positive family. VSP is keyed by variable,
VSM by variable/dimension, VCN by constraint; multiple current tips there are
query conflicts, including semantically identical tips. PIF is port/context/
dimension; PCM endpoint pair/context, each with a single admitted root per key.
PCN, VPA, BHD, STD, TRD, FLD, FMA and FCD admit their documented independent
roots; corrections merge only within a root and preserve its exact subject key.
They must not merge independent corroborating roots to conceal disagreement.

All DAG ancestry must be membership-present and acyclic. Strict withdrawals
PTW/VPW/BHW/STW/TRW/FLW/FMW/FCW require an unsuperseded positive target and
no duplicate withdrawal within the selected membership. A superseded-and-
withdrawn target is invalid there; do not copy REL/RWD's looser rules into them.
Withdrawing a tip does not reactivate its retained superseded ancestor. Only
an explicit reference-closed historical membership excluding later lifecycle
records may make that ancestor current again. Registrations are permanent,
not a DAG to which generic correction/withdrawal tools may be applied.

### 5.4 Currentness is a query predicate, not graph reachability

The key live counterexample to a uniform “pin stale ⇒ everything invalid” rule:
FM's FLD/VPA support row can be `activity='superseded'`, containing lineage
`healthy`, and `current_alignment='exact'`. FM uses exact historical subject
support and reports those three facts separately. When the lineage is inactive,
its alignment becomes unaligned. FM's VSM semantic alignment checks the current
observation-role bodies; an identical-body successor can leave semantic alignment
exact while the pinned edition is superseded. **FM has no new DI applicability
verdict to overwrite.** FC separately requires exact current typed pins and
therefore can be inapplicable in those same worlds.

Similarly STD's declaration can remain declared while upper state classification
refuses an old VCN pin. TRD's endpoint STD pin can remain current even when a
condition beneath that STD changed; TA's classification inputs then need
reevaluation. RTD correction can leave a REL valid under its exact cited old
type while current-label/current-type disclosures change. Always compare the
owning public query fields, retaining the distinct lower conclusions/reasons.

FC's `witness_record_indices` preserve exact old FMA records; its
`matching_fm_current_indices` may point to different same-body current records.
A different healthy current same-body FMA can preserve applicability after the
nominated witness is withdrawn. Conversely, an active changed-body successor
plus an independent old-body root can create cross-root disagreement; the mere
presence of one matching body does not defeat that conflict gate.

## 6. Foreign and carried-result composition dependencies

No model-only reference graph is a complete inventory of all decisions. These
are separate Q/X paths, with independent ledger namespaces and exact cutoffs:

| Layer | Exact public input fields / dependency | Reassessment and boundary |
| --- | --- | --- |
| IB | ANC `anchor` including variable owner; IBA `subject`, `property`, `target_anchor_id`, `applies`, scalar `supersedes`; IBR `retracts`; IBC `closes`/`end`; IBJ `rejected_anchor_id` diagnostic only. Resolution carries `revision`, `via_assertions`, `resolved_target`, `subject_context`; declared-locator discovery carries its explicit summaries. | These are binding-ledger relationships, not kernel records. Corrections/retractions/closures can change bound candidates at the same requested time; replacement needs a new anchor and explicit applicability. Foreign summary/result IDs alone do not supply an entire foreign ledger for graph reconstruction. |
| SPI | SPI `subject`, `property`, `interpretation`, `applies`, `supersedes[]`; SPR `retracts`; SPC `closes`/`end`; SPJ rejected interpretation diagnostic. `PropertyInterpretationResult` carries dimension resolutions and `revision`. | Exact source-property/dimension/time selects interpretation; no edge from equal unit or role token alone. Kernel evidence does not dereference SPI. Full proposed foreign revision changes are outside the model-membership pair. |
| VM / VS | `VariableStateResult.variable_registration`, `owner_registration`, `requested_entity_registration`, `model_revision`, `binding_revision`, candidates' `declaration`/`bound`/`attachment`; VS `state`, `specification_result`, `candidates[].state_candidate`, `ruleset_version`, `as_of`. | Changed registration, VSP or binding-selection domain invalidates reuse for the new request, not the old observation. Supplied full model material lets the reviewer compare the model facts; no globally complete raw/binding truth claim from a summary. |
| ES / CN | ES `value_compatibility`, `semantics_result`, `interpretation_revision`, `candidates[].interpretation`; CN `constraint`, `semantic_compatibility`, `as_of`, `ruleset_version`, `candidates[].semantic_candidate_index`. | Exact CRG/VCN and model/foreign revision bindings must agree. CN verdict requires reevaluation when its inputs/selection change; do not reverse satisfied/violated by traversal. |
| BH | `BehaviorEvaluationResult.behavior`, `participant_sources`, `participant_semantic_results`, indexed participants, cohort and execution fields. | BHD/participant lock, selected ES/VS/source cohort dependencies; no causal link inferred from equality. |
| ST classification | `state`, `condition_sources`, `constraint_evaluations`, `conditions`, exact model/binding/interpretation commitments and `as_of`. | Permanent complete condition set and exact current pinned VCN enforced by existing derivation. New conflicting VCN may matter without appearing in an old positive candidate row. |
| EA | Selection `request.scope`, `horizon_started_at`, `as_of`, selection policy; snapshot `source_material`, `temporal_material`, routes, selection, coverage, fences, issues and fingerprint. | EA has **no model-revision dependency**. A model-only correction cannot stale source evidence or change EA membership. Modified source/cutoff/request requires a separately captured/validated result, not synthetic replay of a model edge. Reuse and seed closure remain intact. |
| Alignment | `request.selection`, `request.compatibility`, `expected_snapshot_fingerprint`; exact occurrence/locator/cutoff and candidate attachment. | VS/model revision changes can require a new alignment even when EA unchanged. Honest multiple matches remain `criterion_evaluation_unavailable` under accepted CS, not forged input. No source reread in result validation. |
| TA | `request.transition`, `from_classification`, `to_classification`, `evidence_alignments`, endpoint cutoffs, context and policy. | Complete governing alignment set and expected fingerprints required; any changed carried input requires recomposition. Endpoint-pattern result is not transition occurrence. |
| FC commissioning / CS | FC full material/governing group + exact CN CRG/VCN/candidate + EA/alignment/VS and independently expected commitments; explicit application policy/version/authority retained by caller. | No repository-owned combined decision record or registry. Caller manifest must identify this composed decision. Reevaluation is not automatic violation, nor a physical measurement-freshness claim. |

For every Q path, distinguish a **selected-record reference** from a
**selection-domain dependency**. A new root with the same exact family key
can change a previously unique result even though the old result did not cite
the new ID. Use the exact owning query request over complete membership to
derive the selector's candidate set, including absence and conflicts; do not
fabricate a record-to-record edge merely from a shared context/variable.

Model-bearing public results also carry an exact model revision. Thus even an
unrelated model append prevents treating an old serialized result as an answer
under the proposed revision. Its declared semantic subject can be unaffected
while the result requires recomputation to be carried in a new-revision join.
This Q membership dependency must be disclosed separately from narrower
semantic support paths; otherwise either false physical impact or unsound
cache reuse follows.

## 7. Application review vocabulary and authoritative consequence derivation

No public DI result class or exported enum is proposed. The following exact
review labels freeze this document's comparisons only. They are not a single
severity ladder or a new lower-layer status. Use separate membership admission,
per-declaration findings, and per-decision reuse rows; findings can coexist
without overwriting each other.

| Label | Exact meaning |
| --- | --- |
| `revision_invalid` | Proposed membership fails actual structural/canonical/reference/lifecycle admission. No ordinary declaration-impact result is derived from the invalid membership. |
| `declaration_stale` | A retained exact mutable support edition is no longer current where the named owning consumer requires that exact current edition. Include the consumer and exact lower support relation; do not call every historical evidence citation stale. |
| `declaration_inapplicable` | Retained historically admitted declaration/body cannot currently govern/apply under the named owning query, with its actual lower conclusion/reasons. Includes FC loss of support; does not pretend FM itself exports an applicability verdict. |
| `lineage_conflicted` | An admitted family's relevant multiple tips/roots prevent its unique conclusion. Preserve same-root conflict versus cross-root disagreement and the lower labels. RTD's prohibited fork instead produces `revision_invalid`. |
| `decision_requires_reevaluation` | A nominated decision's exact input, selection domain, membership, context, cutoff, ruleset or application policy changed. Original result remains historical; proposed verdict is not predicted. |
| `unaffected` | No dependency path in the explicitly complete admitted relation/decision scope, and no owning-query evidence of an effect. Never global, never physical. A semantic-only comparison must explicitly exclude Q revision-binding claims rather than suppress them. |
| `dependency_observed_no_consequence` | A path exists, but before/proposed owning queries preserve the scoped semantic conclusion; retain changed provenance/activity and alternatives. This avoids falsely calling a dependent with an unchanged body “unaffected.” |
| `unknown` | Decision inventory, foreign material, scope/semantics or required owning result is unavailable/unsupported; neither a negative reachability proof nor a predicted consequence is established. |

Input inconsistency or resource exhaustion refuses the review request with
`input_incoherent` or `analysis_limit_exceeded`, distinct from `revision_invalid`.
A review can honestly contain an unaffected declaration, a changed witness
disclosure, and a decision requiring reevaluation; these are different subjects
and claims, not contradictory status values.

Algorithm: reconstruct both complete memberships; validate comparison mode;
derive exact deltas; enumerate typed references and owning query selectors;
requery affected selection domains in both worlds; compare exact lower fields;
derive each nominated decision's reuse obligations; then disclose paths and
findings in canonical order. Do not assign consequence from path length, edge
count, timestamps, authority priority or string equality of serialized results.

Existing result validators verify their own boundaries, not the scope invented
by an application. Summary-only older kernel results must be regenerated via
`ModelQueries` from full material to prove closure/completeness. CN model facts
must be compared to exact model-material queries, not merely trusted because
their local result shape validates. A review manifest independently enumerates
each required query/decision; compare its full expected key set to the result
set so omissions, including no-longer-evaluable decisions, cannot disappear.

## 8. Direct and transitive review scope, bounds and reconstruction

### 8.1 Traversal is a typed explanation, not a consequence engine

For the bounded application recipe, admit only I/E/L/H/S/Q from sections 5–6.
X references terminate at an explicitly labelled foreign frontier unless exact
supported public material and an approved foreign review scope are supplied.
No physical, token-name, lexical, causal or “connected to X” edge is admitted.
Unsupported relation kinds produce `unknown`; a completeness request including
them cannot return `unaffected`.

Record references point to prerequisites. Review traverses their reverse
adjacency, keeping each record-kind/field-path/target-kind label. Selection-domain
nodes are typed existing query requests (family and exact key/context), not
new durable entities. A newly added tip links through the selector that actually
reads it, not to all records mentioning the same variable. Preserve role paths
such as TRD.from versus TRD.to and each distinct FCD→FMA→FLD→PIF path.

Compute finite reachability with a visited-node worklist. Diagnose cycles by
strongly connected components rather than assuming every admitted edge graph
is acyclic; hierarchy may contain declared cycles, and a combined derived
selector/reference graph need not be a correction DAG. An invalid correction
DAG is refused by the lower membership validator first. Cyclic dependency
reachability does not establish an infinite sequence of impacts.

For explanations, disclose **all simple labelled paths** within the declared
budget, plus cyclic-component membership and internal edges. Never repeat a
node within a simple path; do not silently substitute only a first/shortest
path. Deduplicate exact identical edge keys and exact identical path sequences,
not distinct field paths or alternative semantic support. Order edges by
source namespace/kind/ID, exact field path, target namespace/kind/ID; order
paths by edge count then full ordered edge-key sequence. No set iteration or
Python hash values enter serialization.

### 8.2 Bounded capacity experiment, not borrowed production limits

No v1 traversal API or production limits are approved. The proposed *design
review profile* is intentionally small: at most 64 records per before/proposed
membership; 16 changed inputs; 16 explicitly named decision requests; 128
record nodes, 128 derived selector/foreign-frontier/decision nodes (256 total);
512 distinct labelled edges; 512 simple paths across the whole review; depth
64; and 8,192 total edge references across all disclosed paths. Both worlds
and all changed seeds share these budgets, not one budget per seed or result.

These are not TA's limits. The live disposable FC review measured 15 baseline
records / 40 explicit record-or-anchor reference occurrences / 12,604 serialized
material bytes; representative proposed worlds measured 17/46/14,528,
18/57/15,713 and 18/51/14,945. Baseline FC result was 14,692 bytes. Those counts
are capacity observations, not a claim that an untyped string-reference count
is a valid DI semantic graph. The live authoritative model has 36 records.
The 64-record profile therefore contains both that membership and these
single-consumer examples; 512 edges permits the observed reference population
plus labelled selector/identity edges without implying arbitrary model scale.
Path/depth/work caps intentionally refuse dense cases; no worst-case latency
or production scalability has been measured or promised.

For defensive admission of this exploratory profile, require an explicit caller
byte/node/depth budget before receiving untrusted material; illustrative ceiling
is 1 MiB per model material, 4 MiB aggregate review input, 32,768 expanded input
nodes, depth 64. These exceed the measured small material sizes but may reject
otherwise valid lower results, especially EA/TA. They are **not** lower-contract
validity changes and do not constitute a production sizing recommendation.
Requiring the full size range of accepted EA/TA results needs a separate measured
application-capacity decision, not silently importing their maxima.

Every limit is inclusive; charge attempted nodes/edges/path expansion before
allocation. Count shared input appearances and repeated path references against
aggregate work. Crossing any cap refuses the whole review as
`analysis_limit_exceeded`, without truncation, favorable partial paths or a
complete/unaffected label. No hidden defaults or implicit budget renewal.
An owner who needs larger scale must identify the actual consumer payload and
measure it before adopting bounds; this is not a new foundational prerequisite.

### 8.3 Authoritative reconstruction and carry-once rules

Retain one before `ModelQueryMaterial` and one proposed `ModelQueryMaterial`,
each once; overlapping records occur in both because the existing material
contracts require complete independent memberships. Do not invent a deduplicated
cross-revision pool which no accepted validator reconstructs. Query findings
reference those materials rather than add another copy to every path. Preserve
each nominated upper result once as its complete accepted root with its required
nested material; do not flatten or strip CN/TA/alignment material to save bytes.
No new serialized aggregate/result identity is necessary.

Independently bind before/proposed membership, comparison mode, change intent,
decision request inventory and all external commitments. Reconstruct records,
identities, revisions, edges, selectors, paths and consequences from those exact
inputs. Never trust an already-green `model_construct`, `model_copy`, directly
constructed LoadedModel, cached reverse index or supplied consequence flag.
Revision hashes bind model ID and member IDs; record validation binds canonical
content. They do not authenticate a ledger, owner acceptance, source bytes or
foreign records not carried.

Admission must reject wrong kinds, stale content-derived IDs, extra/hidden
fields, duplicate mapping keys, hostile scalar/container subclasses, cycles in
input objects, non-finite numbers and Boolean-as-index/count values before
expensive parsing/reconstruction. Use only supported exact lower types and
strict built-in indices. Recompute row indices as contiguous canonical ranges;
missing, duplicate, extra, reordered, substituted or noncontiguous rows are
invalid. Mapping insertion order may vary; authoritative array order may not.
Do not normalize malformed arrays into validity at the result boundary.

Mixed before/proposed material cannot be silently accepted because names match.
An old result is allowed only as an explicitly labelled before result; a proposed
result must match the proposed model material and exact request. Validate
selectors even for absence/conflict results. No filesystem, store, database,
network, environment, clock, adapter or LLM call is part of result validation.
Store load/replay and any acquisition of new upper results are separate explicit
caller operations. No new DI result validator is implemented by this document.

## 9. Fourteen concrete disposable change examples and valid twins

The live experiments used the existing disposable FC helper world, public
`build_record`, `ModelRevision`, `ModelQueryMaterial`, `.loaded()` and
`ModelQueries`, with no store append and filesystem opening forbidden. They
reconstructed valid before/proposed worlds, not edited green result objects.
Symbolic names below denote those actual valid records and their exact pins;
no fabricated full record hash or committed example identity is introduced.

Base W contains 15 records, applicable FCD D, its retained FMA A, exact CRG C
and VCN V, FLD L, VPA P and measured-actual VSM S. A correction is built through
the public builder retaining every original required field and adding the
family-valid `supersedes`; it never mutates W. E is an independently constructed
same-body FMA root. Each negative case includes its valid repair or control.

| Case | Complete before/proposed change and exact path | Actual consequence / valid twin |
| --- | --- | --- |
| 1. VCN correction | W → W+V2 where V2 supersedes V, even with identical predicate and semantics. Reverse review V ← D.`constraint_declaration_record_id`; selector V2 → current-VCN key → D. | FC is inapplicable with `vcn_not_current`; retained pin stale for FC. Twin W+V2+D2, D2 superseding D and explicitly pinning V2, is applicable. No automatic criterion renewal. |
| 2. FMA body correction | W → W+P2+A2, P2 corrects P and A2 corrects A while pinning P2. D still cites A's historical body. | FC reports `fm_body_not_current` and old typed support not current. Twin add D2 superseding D and designating exact A2/C/V: applicable. A's bytes and witness disclosure remain retained. |
| 3. Healthy same-body preservation | W+E → W+E+withdraw(A). Path A ← D remains a historical witness dependency. | FC remains applicable through healthy E; dependency observed with no applicability consequence. Negative control W+withdraw(A) loses support. Do not claim E rescues W+E+P2+A2: the active changed body and old body disagree and FC remains inapplicable. |
| 4. FLD correction or withdrawal | W → W+L2, or W+FLW(L); path L ← A.`flow_declaration_record_id` ← D. | Correction gives FM superseded/healthy/exact historical support but FC `typed_support_not_current`; withdrawal gives inactive/unaligned support and FC `typed_support_inactive`. Twin original W is applicable; full explicit L2→A2→D2 renewal can use the corrected support. No physical flow change is proved. |
| 5. VPA correction | W → W+P2; P ← A.`variable_port_association_record_id` ← D. | FM reports historical support superseded, not necessarily unaligned; FC becomes inapplicable on the exact-current requirement. Twin case 2's explicit P2/A2/D2 renewal is applicable. Neither variant proves observation at a port. |
| 6. Identical-body VSM correction | W → W+S2 with identical observation-role body and S2 superseding S; S ← A.`variable_semantic_declaration_record_id` ← D. | FM semantic alignment can stay exact; FC `typed_support_not_current` still requires exact-pin renewal. Twin W unchanged remains applicable; explicit new S2 pin/FMA/FCD renewal is the honest route, not token equivalence. |
| 7. Corroboration versus conflict | W+E has two independent equal-body healthy FMA roots. W+A1+A2fork instead has two distinct same-body successors of A. | First applicable; second FC inapplicable with `fm_same_root_conflict`, even if effective bodies match. Same-root merge superseding both tips is the valid conflict-resolution form; time/authority/ID priority is not. |
| 8. Withdrawal and replay | Full W+withdraw(A) is inapplicable. Independently select reference-closed historical W from the retained corpus. | Historical W is applicable again; no append-only record was removed or undone. An asserted append-candidate omitting the withdrawal is invalid mode intent; valid twin explicitly labels historical comparison. |
| 9. Identity replacement | W+VRG(new variable anchor with same display name/owner); old C and A continue to name the old variable. | No silent move; original FC still applicable for the old identity. New downstream CRG/VCN/VPA/VSM/FMA/FCD declarations are required for the new subject if desired. Same-anchor second registration with changed name is refused; valid twin uses a distinct canonical anchor. This proves no installation. |
| 10. Evidence correction, same body | W+A3, A3 supersedes A and changes only owner-declaration evidence, leaving all effective-body fields exact. | FC remains applicable; historical witness A retained, current same body supplied by A3. Provenance changed, not semantic invalidation. Negative twin changing a support pin without renewing D is case 2; editing A under its old ID is refused. |
| 11. Unrelated change | W+REG(U), a new unreferenced entity with distinct identity. No I/E/H/L/S path from U to D's semantic support. | D's scoped applicability is `unaffected`, verified by unchanged conclusion. Its full model-bearing result nevertheless has a different revision and requires recomputation for proposed-revision use; do not omit that Q effect. Control a V correction produces case 1. |
| 12. Commissioning reevaluation | Nominated commissioning decision carries FC/CN/VS/alignment under W; propose W+V2. Path V → FC designation and CN selection → named commissioning join. | Mark `decision_requires_reevaluation`; preserve the old historical CN verdict. No automatic violated↔satisfied reversal. Valid twin retains the identical original request and membership for historical use; unknown/unlisted decisions are not silently declared unaffected. This is a composition obligation, not a newly executed commissioning simulation. |
| 13. Broken hypothetical closure | Explicit candidate membership retains D but omits A. D.`flow_measurement_association_record_id` has no target. | Public ModelQueryMaterial refuses membership; `revision_invalid` for closure, not ordinary stale impact. Valid twin carries A and full support closure as W. In append mode the exclusion independently violates append intent as well. |
| 14. Multi-change interaction | Before W+E. Removing current support by valid withdrawal of A alone preserves E; withdrawal of E alone preserves A. Combined W+E+withdraw(A)+withdraw(E) retains all records but no current same-body FMA. | Each singleton keeps FC applicable; combined FC inapplicable. Both singleton worlds are valid twins proving non-additivity. Full-set reevaluation, not union of singleton conclusions, detects it. |

The tests of these model predicates passed in memory. This does not claim a
new DI engine, a newly implemented transitive traversal validator, or execution
of a changed-source CN/TA workflow. Existing source-backed witness and fixture
artifacts were not regenerated. Complete repair chains mentioned as extensions
must still be admitted through the same public contracts; there is no automatic
repair builder or engineering recommendation here.

### 9.1 Reproducible public in-memory construction pattern

The following runnable design example demonstrates the decisive public seam,
VCN stale-pin repair, same-body preservation and two-change interaction. It
uses existing disposable builders only and performs no file/store writes.

```python
from hashlib import sha256
from unittest.mock import patch
import backend.model_kernel as k
from tests.model_kernel.fc001_slice_a_helpers import world, declaration, replace
from tests.model_kernel.test_flow_measurement_slice_a import withdrawal

records, witness, crg, vcn = world()
designation = declaration(witness, crg, vcn)
base = (*records, designation)

def query(rows):
    ordered = tuple(sorted(rows, key=lambda r: r.record_id))
    ids = tuple(r.record_id for r in ordered)
    model_id = 'di001-disposable'
    revision = k.ModelRevision(
        revision_id='mrv_' + sha256('\n'.join([model_id, *ids]).encode()).hexdigest(),
        model_id=model_id, record_ids=ids, record_count=len(ids))
    material = k.ModelQueryMaterial(revision=revision, records=ordered)
    return k.ModelQueries(material.loaded()).flow_operating_criterion(
        witness.flow_anchor_id, witness.variable_anchor_id,
        witness.participant_port_anchor_id, witness.context, witness.orientation)

def forbidden(*args, **kwargs):
    raise AssertionError('unexpected filesystem access')

with patch('builtins.open', forbidden), patch('pathlib.Path.open', forbidden):
    assert query(base).subject.conclusion == 'applicable'
    successor = replace(vcn, supersedes=(vcn.record_id,))
    changed = query((*base, successor))
    assert changed.subject.conclusion == 'inapplicable'
    assert 'vcn_not_current' in changed.subject.body_groups[0].reasons
    renewed = declaration(witness, crg, successor,
                          supersedes=(designation.record_id,))
    assert query((*base, successor, renewed)).subject.conclusion == 'applicable'
    equal = replace(witness, note='independent equal-body root')
    first, second = withdrawal(witness), withdrawal(equal)
    assert query((*base, equal, first)).subject.conclusion == 'applicable'
    assert query((*base, equal, second)).subject.conclusion == 'applicable'
    assert query((*base, equal, first, second)).subject.conclusion == 'inapplicable'
```

## 10. Alternatives and architecture ownership

| Alternative | What it could honestly do | Decision |
| --- | --- | --- |
| Current reverse-dependency disclosure only | Enumerate direct typed references/ancestry under one membership, including provenance, without predicting changes. | Already reconstructible by a public field scan and existing reverse indexes; insufficient alone for the asked before/proposed consequences. No milestone. |
| Pure hypothetical candidate-membership evaluator | Validate proposed canonical membership and run owning queries without appending. | Already possible through ModelRevision/ModelQueryMaterial/loaded/ModelQueries; a new evaluator would duplicate a public seam. |
| Read-only application composition of existing results | Compare two complete memberships, exact typed paths and a nominated complete decision set. | **Recommended outcome 1.** No new code approved; exact scope and external decision inventory belong to the named application consumer. |
| New model-kernel reverse-dependency query surface | Centralize field enumeration and perhaps reverse maps, not upper decisions. | No missing integrity property demonstrated. It cannot discover CN/TA/application consumers without reversing import direction. Convenience and possible scaling benefit need evidence, not an assumed milestone. |
| Sibling read-only `model_impact` | Could consume public model/result contracts and enforce a newly designed aggregate. | Rejected here: no attack requiring that aggregate was demonstrated. It would need a decision-family registry, application completeness semantics and measured bounds, while adding no currently missing lower fact. |
| Durable dependency records | Persist duplicate edges already present in canonical records or hardcode application consumers into a second ledger. | Rejected presumptively and concretely: correction divergence/dual authority risk without a new durable engineering fact. Application inventory retention is not a model dependency ledger. |
| Prerequisite repair or defer | Needed if a concrete required property is missing, rather than if an app simply lacks a policy/inventory. | Outcomes 4/5 not recommended: the bounded model/decision review question is answerable now; broader unknown application/foreign scope must remain explicitly unknown. |

Architecture owner: the engineering change-review application, above public
kernel queries and whichever accepted result families it explicitly consumes.
No code or new owner package is selected. Kernel imports remain restricted to
system identity, standard library and Pydantic; no source, temporal, EA, binding,
adapter or upper composition imports. A future sibling, if independently
justified, may consume public lower contracts only and must not open stores
during validation or own another truth system. No LLM-inferred path becomes
authoritative; a suggested engineering dependency requires explicit separately
accepted records of the appropriate kind, not acceptance of this proposal.

## 11. Threat model and acceptance twins

Attacker controls supplied material and claimed paths/results, not the caller's
independently retained before/proposed/request commitments. A fully replaced
expected context is outside this content-binding proof; neither hashes nor
public validation authenticate engineering authority or omitted foreign bytes.

| Attack | Required handling | Valid twin |
| --- | --- | --- |
| T01 Record-kind substitution | Reconstruct discriminated records and exact target-kind closure; reject VCN/FMA/withdrawal lookalikes. | Same-kind, correctly hashed exact target with complete closure. |
| T02 Correction presented as replacement or vice versa | Compare actual supersedes/identity fields and mode; no inferred identity transfer. | New canonical replacement registration with explicitly new dependents, or same-key valid correction retaining ancestor. |
| T03 Evidence edge presented as mutable semantic support | Preserve E versus H/S; query consequences only under owning rules. | Case 10 provenance-only same-body change retains FC applicability. |
| T04 Semantic support presented as causality | Reject physical/causal conclusion; report typed dependency only. | Exact VCN→FCD pin path with applicability/reevaluation disclosure and no physical verdict. |
| T05 Cross-context leakage | Admit exact query family/key/context/role, not union by shared variable/port. | Two separately named contexts with separate queries and findings. |
| T06 Mixed before/proposed revisions | Bind every material/query/result to its role and exact expected membership. | A correctly labelled historical before result remains valid only for before. |
| T07 Missing proposed membership or omitted support bytes | Do not infer after from a seed ID; fail admission/unknown input availability. | Complete proposed material including historical closure, even if a support is non-current. |
| T08 Silent deletion from append-only ledger | Append mode rejects excluded IDs; never call deletion withdrawal. | Explicit historical comparison of a closed subset, or actual retained target plus valid withdrawal record. |
| T09 Same-name identity substitution | Full canonical anchor/registration comparison, no name matching. | New distinct anchor preserving old identity's dependents. |
| T10 Exact body confused with exact record ID | Historical witness closure requires its exact ID; current FM body support may be supplied by another valid same-body root. | Case 3 retains old witness and healthy equal-body root; omitting old witness still refuses. |
| T11 Current versus historical support confusion | Recompute membership-relative activity and owning currentness predicate; preserve historical fields. | FM superseded/healthy/exact disclosure coexists with FC inapplicability; historical W restores its own prior conclusion. |
| T12 Conflict resolved by timestamp, authority or ID | Preserve family conflict/disagreement; only accepted DAG operations can resolve it. | Independent corroborating healthy roots; or valid same-root merge of all conflicting tips. |
| T13 Incomplete multi-change interaction | Evaluate complete combined membership, including secondary support/root effects. | Case 14's two valid singleton worlds and different combined result. |
| T14 Cycles and path explosion | Lower DAG cycles refuse; derived relation cycles use visited/SCC logic; aggregate path/work cap refuses, never truncates into “unaffected.” | Finite cyclic relationship disclosure with no causal claim; bounded acyclic labelled paths fully enumerated. |
| T15 Duplicate/reordered/extra/missing paths | Reconstruct exact canonical edge/path set; reject forged ordering/cardinality or noncontiguous indices. | Different mapping insertion order with identical canonical arrays. |
| T16 Resource-limit bypass | Preflight raw bytes, expanded nodes, depth and per-edge/per-path aggregate work; charge shared content repeatedly. | At-cap admitted small review; one-over typed `analysis_limit_exceeded`, not partial success. |
| T17 Forged consequence classification | Requery both materials and recompute exact owner-specific findings, not a severity sort over paths. | Dependency exists but conclusion preserved through E; report no consequence, not false invalidity. |
| T18 Hidden store/file/network/clock access | Validation/reconstruction must be pure; explicit lower acquisition happens outside. | In-memory public model reconstruction with file opening forbidden, as executed here. |
| T19 Nondeterministic ordering | Sort full typed keys and paths; stable lower canonical material; compare across hash seeds. | Shuffled dictionary insertion yields identical ordered report projection. |
| T20 Unaffected record falsely marked impacted | Require an actual typed relation/selector path and scoped owning-query comparison; no shared-name edges. | Unrelated REG has no semantic path to D; separately disclose exact-revision Q reuse effect. |
| T21 Impacted decisions silently omitted | Compare returned decision keys to independently supplied complete manifest, including refused/unknown results. | Exact full manifest retained; unavailable decision gets an explicit unknown/reevaluation row. Unlisted application decisions are outside coverage, never globally unaffected. |
| T22 New competing root omitted from an old positive pin graph | Recompute complete selector candidate population under proposed membership. | New same-key root shown as corroboration or conflict according to the owning query; unrelated key excluded. |
| T23 Forged model_construct/model_copy, cached LoadedModel or stale content IDs | Reconstruct full public material; no trusting cached maps, hidden extras or copied green rows. | Public build_record then full membership validation with unchanged accepted content. |
| T24 Boolean indices/counts, hostile scalar subclasses, duplicate JSON keys | Exact-type admission before conversion or callback; reject ambiguity. | Ordinary integer zero at a genuine index and valid Boolean only in a Boolean field. |
| T25 Foreign citation or summary used to claim foreign completeness | Keep X frontier; require independently supplied supported foreign context or report unknown. | Kernel's declared foreign citation stays historically disclosed without source/binding truth claim. |
| T26 Old commissioning verdict automatically reversed | Mark new-request reuse as requiring reevaluation and retain original exact CN verdict. | Independently recomputed result may remain the same; DI never chooses or predicts that verdict. |

This matrix specifies checks an adopting application must actually enforce;
it is not a new tested DI validator. None of these attacks requires a new
backend contract when complete public model material, owning queries and the
independent application request inventory are supplied. A consumer omitting a
required check is not a newly missing public integrity field.

## 12. Original objectives, missing stronger capabilities and owner gates

| Original objective | Contribution of the bounded review | Confidence / exclusion |
| --- | --- | --- |
| 1. What exists and how is it connected? | Makes explicit declared dependency paths reviewable, using existing facts. | Strong for scoped model references; no new physical connectivity or backend capability. |
| 2. Current state of this system? | Discloses model support currentness/applicability and decision reuse requirements under exact memberships. | Partial; no physical state/freshness/health. |
| 3. Why behaving this way? | Explains dependency-based refusal or staleness, not physical cause. | Foundational only; no diagnostic hypotheses/mechanisms. |
| 4. Next best measurement/test? | May reveal a decision needing reevaluation; no measurement selection. | Foundational only, unchanged; no test ranking or utility model. |
| 5. What would be affected by a component/parameter/software change? | Exact declaration/support/selection and named decision dependencies can be reviewed before an explicit proposed membership is accepted. | Partial and bounded. Stale support is not changed behavior, new identity is not installation, reachability is not causality, reevaluation is not predicted result. |
| 6. Smallest valid change set to desired state? | Can reject a supplied structurally invalid set; does not generate or minimize one. | Absent for planning. No goals/actions/effects/cost or optimality. |
| 7. Observed/calculated/inferred/assumed/unknown? | Separates canonical declaration facts, calculated query differences, application completeness assertions and unknown foreign scope. | Partial overall; traceable within supported scoped results. |

Missing stronger capabilities: physical impact propagation needs validated
physical influence semantics and installed configuration evidence; behavioral
simulation needs executable domain models/parameters and validation oracles;
causal diagnosis needs hypotheses/mechanisms/intervention distinctions; risk
and safety need hazards, exposure, uncertainty and authority; cost/schedule
needs explicit resources, tasks, durations and costs. Proposed-change validation
is already available for structural model membership, but operational feasibility,
engineering correctness, owner approval and externally backed source changes
are not established by it. Desired-state planning additionally needs explicit
goals, available actions, effects, constraints and an optimization criterion.
No graph traversal can supply these missing semantics.

No implementation slices are proposed because outcome 1 is selected. If a
later owner finds an actual omission/integrity or measured scaling problem,
the new proposal must name the failing public join and demonstrate why complete
material plus explicit application scope cannot prevent it. Do not reserve
ADR-0023 or a `model_impact` package in anticipation.

Unresolved owner/application decisions: accept/reject this no-new-milestone
finding after the separately authorized challenger; identify the exact inventory
and completeness authority of decisions the change-review workflow will retain;
choose append-candidate versus historical comparison per request; identify any
required foreign ledger changes rather than treating them as kernel references;
and approve measured application capacity if the small exploratory profile is
insufficient. These decisions authorize no hidden defaults, new engineering
dependencies, runtime implementation or authoritative fixture append here.

## 13. Verification, skill use and stopping boundary

Fresh baseline assertions checked exact HEAD/origin equality, latest subject,
accepted reconciliation/CS status, clean tracked tree, live model/revision,
236 exports, zero FCD/FCW, unique accepted ADR sequence and protected digests.
The design used live source/field/index inspection and valid in-memory model
worlds, with public material reconstruction and filesystem opening forbidden.
The initial disposable identity probe omitted required registration metadata;
it was corrected to preserve the existing registration's required fields through
the public builder. This was a probe-construction error, not a baseline or
production defect. The corrected model scenarios passed.

Final checks cover this proposal's numbered sections, exact ending marker,
fourteen examples, threat/twin coverage, local links, runnable public example,
hash-seed determinism for that example's public results, whitespace and the
one-file working-tree allowlist. These are design/documentation checks, not a
new production test suite, full repository run, generic traversal performance
test or end-to-end changed-source commissioning simulation. Protected repository
artifacts are not regenerated or modified.

Repository brainstorming informed the necessity comparison and rejection of
premature contracts; verification-before-completion informed fresh checks and
limited claims. The user's exact path/design-only/no-commit/stop instructions
override the skills' default spec path, commit and implementation handoffs.
Codex worked alone; no delegated or external challenger audit was run.

Only this proposal file is written in the repository. No existing file, ledger,
fixture, identity, canonical record, membership, generated artifact, test or
production implementation is changed. No branch, commit, push, merge or history
operation occurs. ADR-0023 remains absent and unallocated. Stop here; one
independent challenger audit may be authorized separately by the owner.

END OF DI-001 CODEX LEAD PROPOSAL
