# model_kernel

The MK-001 typed entity/relationship kernel: an append-only ledger of
explicit model knowledge over canonical `system_identity` anchors, with a
containment-derived hierarchy view. The bridge target of:

```text
data_sources → temporal_state → identity_binding → model_kernel
                        system_identity ────────→ model_kernel
```

Spec: `docs/superpowers/specs/2026-08-08-mk001-model-kernel-design.md`;
decisions: `docs/adr/0007-model-kernel-typed-graph-ledger.md`.

Accepted additive kernel decisions now extend through explicit variables,
constraints, ports, variable-port associations, behavior, state, transition,
and flow records. Their accepted decisions are ADR-0012 through ADR-0018 in
`docs/adr/`; ST-002 remains transition-declaration-only and FL-001 remains
flow-declaration-only.

## Boundary

Runtime code imports only `system_identity`, the standard library, and
pydantic (AST-enforced by test); it never reads or writes any binding,
temporal, or evidence store and operates identically when those stores do
not exist. The kernel provides no anchor-creation API: demo anchor IDs are
externally allocated fixture constants declared through `AnchorDeclaration`
records in an identity-binding ledger, and registrations embed those
`EntityAnchor` values verbatim. The kernel cannot prove at runtime that an
embedded anchor was declared — committed fixtures are seam-verified in CI;
runtime model sets use the documented external verification procedure.

## Semantics worth knowing

- **Behavior is explicit model knowledge** (BH-001 Slices A and B): an
  evidence-bearing permanent `BehaviorRegistration` binds one stable `bhv_`
  identity to exactly two distinct, unordered, role-free registered variables
  and the sole v1 family `exact_numeric_equality`. Cross-owner pairs are
  permitted only through that explicit claim; common ownership creates
  nothing. Evidence-bearing `BehaviorRuleDeclaration` records carry exact
  `AssertionContext`, participant semantic locks, the minimal equality rule,
  and `same_acquisition_cohort` as a future evaluation basis. Corrections form
  membership-relative multi-root DAGs keyed by behavior anchor and exact
  context; same-root forks remain visible, cross-root convergence is rejected,
  and `BehaviorRuleWithdrawal` retracts only a current tip. Slice B adds
  exactly `behavior()`, `behavior_declaration()`,
  `behaviors_involving_variable()`, and `behavior_assertion()` as read-only
  queries over injected `LoadedModel` material. Their carry-once results
  disclose permanent registration, exact-context lifecycle, same-root fork
  conflict, identical-effective-body independent-root corroboration,
  cross-root disagreement, inactivity, ancestry, withdrawals, and historical
  revival without selecting a winner or inferring behavior. Authoritative
  result validation reconstructs records, membership, indices, lifecycle,
  effective-body grouping, and deterministic ordering without a store or
  filesystem. Slices A and B add no evaluation, numeric comparison, port/VPA
  meaning, causality, flow, control, safety claim, or fixture record.
- **Variable-to-port association is explicit** (VP-001 Slices A and B): an
  evidence-bearing `VariablePortAssociation` relates one registered variable
  to one registered port in an exact assertion context only when both are owned
  by the exact same registered entity. Shared ownership never creates the
  claim. Independent roots corroborate; correction forks and convergence remain
  within one root; `VariablePortAssociationWithdrawal` retracts only a current
  positive tip membership-relatively. The claim says nothing about observation
  location, ownership transfer, values passing through a port, topology,
  compatibility, flow, behavior, control, causality, correctness, or safety.
  Slice B adds four read-only exact/reverse/assertion queries with one complete
  selected membership carried per result and index-only nested disclosures. It
  adds no model-state composition or fixture record.
- **Ports are explicit model identities and claims** (PT-001 Slice A): a pure
  `PortAnchor` is permanently registered to one entity by an evidence-bearing
  `PortRegistration`; three independent interface dimensions, positive
  unordered 2–64-port topology hyperedges, and explicit compatibility claims
  use membership-relative correction DAGs and the generic PT withdrawal.
  Duplicate endpoints are rejected, connection roots may corroborate, and PCM
  citation validity is structural rather than chronological. Domain and
  interface-type tokens carry bounded qualified system, edition, and code
  identifiers plus their serialized dimension discriminator. Comparison is
  exact over all four fields; the kernel performs no vocabulary inference,
  equivalence, or conversion. Slice A adds contracts, canonicalization,
  validating storage, and immutable indexes; Slice B adds the accepted
  read-only PT queries. Traversal remains excluded. The bounded ten-record
  synthetic fixture is authorized only in Slice C.
- **Variable meaning is explicit and per dimension** (ES-001):
  `VariableSemanticDeclaration` records quantity-kind and observation-role
  identity tokens independently. Each `(variable, dimension)` lineage is a
  multi-parent correction DAG; conflicts remain queryable, full-tip
  supersession converges them, and replay is membership-relative. Tokens assert
  identity only—no ontology, dimensional algebra, convertibility, behavior, or
  source meaning. Evidence-reference closure now applies uniformly to every
  evidence-bearing `rel_`, `vsp_`, and `vsm_` claim.
- **Variable constraints are explicit model claims** (CN-001 Slice A): an
  evidence-bearing permanent `ConstraintRegistration` binds one stable `con_`
  anchor to one registered variable. Evidence-bearing
  `VariableConstraintDeclaration` records carry exact quantity-kind, role, and
  unit token locks plus a lower, upper, or interval decimal predicate. Their
  multi-parent correction DAG is keyed only by constraint anchor; conflicts,
  convergence, superseded history, and replay are membership-relative and
  never ranked. Both `crg_` and `vcn_` model-record evidence is uniformly
  reference-closed. Evaluation belongs to the read-only
  `backend.constraint_evaluation` composition layer.
- **Variables are membership, not structure or state** (VM-001): a
  `VariableRegistration` embeds one canonical `VariableAnchor` verbatim.
  Ownership is identity (`anchor.entity_anchor_id` — no `variable_of`
  edge); the owner entity must be registered in the same revision
  (reference-closed, including replay subsets); one registration per
  variable anchor (duplicates rejected whether embedded fields agree or
  conflict — never tie-broken); variables never appear in hierarchy views;
  `variable()` / `variables_of()` answer membership with structured
  absence. Like entity registrations: no lifecycle, no correction path,
  no units, no datatype, no meaning, no state.
- **Registrations have no lifecycle**: no supersession, no withdrawal, no
  path that alters an embedded anchor field. Two distinct registrations for
  one anchor invalidate the revision.
- **All relationship types are data** (`contains` and `instance_of`
  included). Type identity is a lineage named by `type_name`; supersession
  preserves `{type_name, directionality, hierarchy_semantics,
  context_requirement}`; exactly one current definition per name.
  Assertions are judged by the exact definition they cite and stale-marked
  when it is superseded — never retro-invalidated.
- **Validating append**: every supplied record is structurally revalidated
  from serialized field data at the public boundary (a record class alone
  proves nothing — `model_copy`/`model_construct`/stale instances bypass
  validation and can be rehashed), then `append` fully validates the
  current set and the prospective set before an atomic staged promote —
  absent filesystem tampering, the on-disk ledger is a valid revision after
  every successful append. Identical re-append is a validated no-op that
  still fails if any sibling is corrupted. Single-writer, honestly stated.
- **Public inputs are validated at every entry point**: query arguments
  (anchor id, type name, direction, lifecycle view →
  `MODEL_VIEW_INVALID`, assertion context → normalized mappings or
  `MODEL_CONTEXT_INVALID`) and store arguments (set directory, record
  collection, model id, replay membership) alike. Malformed input is never
  a silently empty answer, and **every operational public entry point of
  the kernel — queries, `ModelStore` construction, `append`, `load`,
  `replay`, `validate_record_collection`, `build_record`, and
  `ModelQueries` construction — fails through the `ModelKernelError`
  tree**: no `ValidationError`, `AttributeError`, `TypeError`, `KeyError`,
  `UnicodeError`, `OSError`, serializer error, or warning escapes as the
  public outcome. Direct construction of the pydantic contract models
  (`EntityRegistration(...)` and friends) is the one deliberate carve-out:
  it follows pydantic's normal `ValidationError` contract.
- **Absence is structured**: `RelationshipsResult.status` distinguishes a
  registered entity with no matching edge from an anchor unknown to the
  revision.
- **Supported surface**: import from `backend.model_kernel` (see
  `__all__`); canonicalization internals, collection validation, and the
  hierarchy projection are private implementation details.
- **Contention is surfaced, malformation invalidates**: distinct-parent/
  same-child conflicts and cycles are structured query results with full
  candidate/assertion disclosure, never resolved by recency or authority;
  dangling references, tampering, duplicate registrations/current names,
  endpoint-kind and context violations invalidate the complete revision.
- **Traversal is deliberately asymmetric**: parent conflicts block upward
  queries (`conflicted`/`partial`) but annotate — not block — downward
  traversal (`multiple_parents`); cycles block both directions.
- **Strict context equality**: every assertion carries a required
  lifecycle-view or view-independent context matching its type; queries
  match one context exactly, never a union; mismatches are typed errors.
- **Evidence explains every edge**: discriminated typed references,
  canonicalized (order- and duplication-insensitive); `model_record`
  references are verified in-revision, all foreign kinds are labeled
  `declared_reference` and never dereferenced.
- **Revisions replay**: `mrv_` revisions are computed-only (never stored);
  `replay(record_ids)` validates pattern-checked, reference-closed subsets
  against the still-present files, with membership-relative currentness.
  Membership input is validated before any member path is constructed;
  then store availability is probed before member reads. Empty membership
  is a valid revision only over an available model store; it is not
  evidence that a missing store is empty (`MODEL_STORAGE_FAILURE` when the
  records directory is gone, replaced, or unreadable). Exact-subset replay
  never requires unrelated ledger members to validate.
- **Cleanup is best-effort**: if promoting a staged record fails and
  removing the staging temp then fails too, harmless staging residue may
  remain — it never masks the typed `MODEL_STORAGE_FAILURE` and never
  corrupts a later `load`.

## Verification

```bash
.venv/bin/python -m pytest tests/model_kernel/   # focused suite
.venv/bin/python -m pytest                       # full repository suite
```

## Known limitations

No kernel correction path for registrations; registrations and type
definitions are irrevocable (no withdrawal); a lineage may end with no
active assertion; disagreement detection exists only for hierarchy types;
no time-varying structure (`rwd_` never means "stopped being true at T");
runtime registration↔declaration consistency is procedural; no global
cross-set anchor uniqueness at runtime; no knowledge-time revision queries;
single-writer stores; no fsync-grade durability claim. Validating append
is O(N²) to build an N-record ledger — accepted for MK-001 scale. The
typed-failure translation catches an enumerated exception set: a hostile
in-process class whose metaclass raises outside it can still surface that
exception, and exception `__cause__` chains can carry raw payloads into
full tracebacks (public messages stay clean). PT-001 complete, owner accepted,
adversarially reviewed, and dual-clean-checkout verified. Slice A is owner
accepted. The qualified-token repair is owner accepted. Slice B is owner
accepted. The public-contract repair is owner accepted. The accepted Slice B
HEAD is `ec9ea7d8c20016e267fae16a2554d5e7f1a0ebce`. Slice C is owner accepted.
The accepted PT-001 membership contains exactly 28 records. Its model revision is
`mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2`.
The deterministic artifact SHA-256 is
`53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`.
Their public results are `PortLookupResult`,
`EntityPortsResult`, `PortInterfaceResult`, `ExactConnectionSetResult`,
`PortConnectionsResult`, `SharedConnectionsResult`,
`PortAssertionDisclosureResult`, and `InterfaceCompatibilityResult`.
Topology admission, topology conclusion, port/owner registration, assertion
activity, lineage health, and compatibility endpoint admission are separate
typed findings. The queries operate only over an injected `LoadedModel`, carry the
complete selected membership once for authoritative reconstruction, and perform
no traversal, store access, or writes. The bounded synthetic fixture is limited
to the implemented Slice C demonstration. Richer
predicates beyond CN-001's exact numeric bounds
also remain future work.

VP-001 complete, owner accepted, adversarially reviewed, and
dual-clean-checkout verified. The final implementation HEAD before the
administrative acceptance commit is
`82fcb93b233db180d5d2d6c54d465dad390f08a5`.
Slice A is accepted at
`60b739182e423a05eac7f3c531145d90c65fe9bc`; it adds only role-free positive
associations with strict same-owner admission, independent corroborating roots,
and dedicated `vpw_` withdrawals. Slice B is owner accepted at
`81179700513bb671cf9955c6a5d7163e3bcc7e1b`. It adds only the four accepted
read-only kernel queries and authoritative carry-once result contracts. Slice C
is confined to the read-only model-state layer; displaying variable state
beside a port does not mean the observation occurred at, originated at,
travelled through, or describes the port. Slice D
adds exactly one parentless `vpa_` and no `vpw_`, correction, or second root.
The explicit final VP / pre-BH membership contains 29 records at
`mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652`;
the explicit 28-record PT membership remains unchanged. The VPA is
`vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49`,
its stored-file SHA-256 is
`95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e`, and
the deterministic VP artifact SHA-256 is
`a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`.
The accepted PT artifact SHA-256 is
`53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`.

BH-001's corrected final design and Slice A are owner accepted. Slice A is
accepted at `57edec37b40c5da0c300cc1333fbb3cf5d7bb41a`. Slice B is owner accepted at
`05177f7306ce745d093bd5f11abafc13a6274d0f`. Its preimplementation
discrepancy is owner accepted at
`eedae19a9b2542958f44e66af7117a981c7faeef` and all four contract questions
are resolved without changing kernel contracts. BH-001 Slices A, B, and C are
owner accepted. Slice C is accepted at
`8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521`. The Slice D variable-anchor
minter discrepancy is owner resolved and the deterministic pre-append contract
at `0905de0` is owner approved. The bounded authoritative append and final
verification are authorized for exactly anchors
`var_ab2d312466054c20b0ac764e9bc0114e` and
`bhv_80e21f1682e449ca9c65a5e2ee051ea0`, revision
`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`,
and the 122406-byte pre-append candidate disclosure artifact at SHA-256
`4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`.
Slice D is implemented and adversarially reviewed. The current demo is the
explicit 32-record revision above and adds exactly one VRG, one BRG, and one
parentless BHD to the explicit 29-record predecessor. It adds no BHW,
correction, fork, second root, specification, semantics, binding, source, or
temporal evidence. The artifact's candidate/proposed scope fields remain
historical rehearsal evidence and do not describe the current repository
state. BH-001 complete, owner accepted, adversarially reviewed, full-suite
verified, and dual-clean-checkout verified. The accepted evaluator
demonstration remains `not_executed` and asserts no observed equality or
real-machine truth.

ST-001's corrected final design is owner accepted and Slice A is owner
accepted. Slice A adds only the foundational ledger contracts:
permanent entity-scoped `StateRegistration` (`srg_`), exact-context
`StateDeclaration` (`std_`), and minimal current-tip
`StateDeclarationWithdrawal` (`stw_`). A registration permanently fixes one
`all_of_constraints` set; a declaration pins one exact VCN per permanent
constraint and fixes `independent_latest_at_or_before_cutoff` as its later
classification basis. State records remain explicit evidence-bearing model
knowledge. Slice A performs no constraint evaluation or temporal
classification, does not infer state from observations, and does not implement state transitions.
ST-002 Slice A is owner accepted and adds declaration-only transition
foundations: permanent evidence-bearing `TransitionRegistration` (`trg_`),
exact-context `TransitionDeclaration` (`trd_`) with exact from/to STD pins, and
minimal current-tip `TransitionDeclarationWithdrawal` (`trw_`). Both endpoint
states must have the exact registered subject, self-transitions and duplicate
ordered endpoint identities reject, and correction DAGs support independent
roots, same-root fork convergence, withdrawal, and historical replay. Slice A
adds no assessment, occurrence, fixture identity, or authoritative ledger
record. ST-002 Slice B adds exactly four read-only query families for owner
validation: `transition()`, `transition_declaration()`,
`transitions_of_entity()`, and `transition_assertion()`. Their frozen results
carry complete `ModelQueryMaterial` once, use strict indices in nested rows,
reconstruct every field authoritatively without store or filesystem access,
and reuse the accepted kernel ST derivations for endpoint state conclusion and
exact pinned-STD activity. The queries disclose registration, exact-context
transition declaration lifecycle, effective-body agreement, endpoint pin
alignment, exact-subject collections, and assertion activity only. They do not
assess, detect, or assert occurrence and accept no observation, source, cutoff,
classification, trigger, guard, action, or state-machine input.
Slice B adds exactly four read-only `ModelQueries` methods: `state()`,
`state_declaration()`, `states_of_entity()`, and `state_assertion()`. Their
frozen results carry `ModelQueryMaterial` exactly once, disclose canonical
roots, tips, withdrawals, effective-body agreement, assertion activity, and
exact-context lifecycle, and authoritatively reconstruct every derived field
without a store or filesystem. Identical independent healthy roots
corroborate; same-root forks and differing active effective bodies remain
conflicted; inactive roots remain visible. IDs order disclosure only and
never select a winner. Slice B is owner accepted at
`23eca10a52c0124d22b4e90d80bef952ef5f9381`. The immediately preceding gate
was: ST-001 Slices A-D are implemented and verified; Slice D final owner
acceptance is pending. ST-001 is now complete, owner accepted, adversarially
reviewed, full-suite verified, and dual-clean-checkout verified at
implementation HEAD `0f05903af4f11fd94d6e6987247ceb9795faebd6`. The accepted
completion-report SHA-256 is
`2ccc501a4ff7c930518e75adc6f991cbb585637e04dbd768bca713cfbcce24b3`.
Slice C is accepted at `f2c6e4e12c3004615e3b0a6f321f6c2b3edec7d6`. The Slice C classifier
is a read-only upper-layer composition and does not alter these kernel query
contracts.

The accepted ST-001 historical membership is the exact 34-record revision
`mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`
with one SRG, one parentless STD, and zero STW records. It contains zero
TRG/TRD/TRW records. The accepted 32-record BH-001 revision remains an explicit historical
membership. ST-002 Slices A and B add no authoritative transition record;
assessment and occurrence remain excluded.
No query infers state from a
constraint, observation, hierarchy, port, VPA, behavior, name, or ownership.
Final acceptance changes no kernel contract, record identity, canonical byte,
membership, or query result and adds no STW.

FL-001 Slice D adds exactly the frozen FRG followed by its parentless FLD,
producing the exact 36-record revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
The current ledger contains one FRG, one FLD, zero FLW, and still zero
TRG/TRD/TRW. The 34-record revision above remains the explicit predecessor.
The four flow queries disclose registration, exact-context declaration
lifecycle, exact pinned PT support, incident port roles, and assertion
lineage. They do not infer adjacency, traversal, physical flow, activity,
occurrence, observation, command, quantity, conservation, behavior, cause,
safety, health, correctness, diagnosis, or recommended action. FL-001 Slices
A, B, and D are owner accepted, Slice C is absent from v1, and FL-001 is
complete, adversarially reviewed, full-suite verified, and
dual-clean-checkout verified at implementation HEAD
`fe3b15a3caf77974a795dad5b04c0a35abee37b4`.
