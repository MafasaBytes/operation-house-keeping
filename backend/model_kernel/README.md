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
The current demo ledger contains 29 records at
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
accepted at `57edec37b40c5da0c300cc1333fbb3cf5d7bb41a`. The current committed demo
remains the accepted 29-record VP revision and contains zero `brg_`, `bhd_`, or
`bhw_` records. Slice B is owner accepted at
`05177f7306ce745d093bd5f11abafc13a6274d0f`. Slice C is owner-authorized but
not yet implemented. Slice D has not started.
